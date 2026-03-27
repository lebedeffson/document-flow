<?php

header('Content-Type: application/json; charset=utf-8');

function respond($payload, $status = 200)
{
    http_response_code($status);
    echo json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT);
    exit;
}

function load_payload()
{
    $payload = json_decode(file_get_contents('php://input'), true);
    if (is_array($payload))
    {
        return $payload;
    }

    return $_POST;
}

function resolve_php_cli_binary()
{
    $candidates = array_filter([
        defined('PHP_BINARY') ? PHP_BINARY : '',
        defined('PHP_BINDIR') ? rtrim(PHP_BINDIR, DIRECTORY_SEPARATOR) . DIRECTORY_SEPARATOR . 'php' : '',
        '/usr/local/bin/php',
        '/usr/bin/php',
        'php',
    ]);

    foreach ($candidates as $candidate)
    {
        if ($candidate === 'php')
        {
            return $candidate;
        }

        if (is_file($candidate) && is_executable($candidate))
        {
            return $candidate;
        }
    }

    return 'php';
}

function build_job_runs($job, $payload)
{
    $definitions = [
        'service_requests' => [
            'script' => __DIR__ . '/scripts/sync_service_requests.php',
            'args' => [
                'request_id' => '--request-id=%d',
                'force_all' => '--force-all',
            ],
        ],
        'projects' => [
            'script' => __DIR__ . '/scripts/sync_project_documents.php',
            'args' => [
                'project_id' => '--project-id=%d',
                'force_all' => '--force-all',
            ],
        ],
        'pull_bridge' => [
            'script' => __DIR__ . '/scripts/pull_bridge_updates.php',
            'args' => [
                'request_id' => '--request-id=%d',
                'project_id' => '--project-id=%d',
                'doc_card_id' => '--doc-card-id=%d',
                'only_linked' => '--only-linked',
            ],
        ],
    ];

    if ($job === 'all')
    {
        return [
            ['job' => 'service_requests', 'definition' => $definitions['service_requests']],
            ['job' => 'projects', 'definition' => $definitions['projects']],
            ['job' => 'pull_bridge', 'definition' => $definitions['pull_bridge']],
        ];
    }

    if (!isset($definitions[$job]))
    {
        respond([
            'error' => 'Unknown sync job',
            'job' => $job,
            'allowed' => array_merge(array_keys($definitions), ['all']),
        ], 400);
    }

    return [
        ['job' => $job, 'definition' => $definitions[$job]],
    ];
}

function run_php_script($job, $definition, $payload)
{
    $command = [
        resolve_php_cli_binary(),
        $definition['script'],
    ];

    foreach ($definition['args'] as $key => $arg)
    {
        if (!array_key_exists($key, $payload))
        {
            continue;
        }

        $value = $payload[$key];
        if (is_string($arg) && strpos($arg, '%d') !== false)
        {
            $intValue = (int) $value;
            if ($intValue > 0)
            {
                $command[] = sprintf($arg, $intValue);
            }
            continue;
        }

        if ($value)
        {
            $command[] = $arg;
        }
    }

    $commandLine = implode(
        ' ',
        array_map(
            function ($part)
            {
                return escapeshellarg((string) $part);
            },
            $command
        )
    );

    $descriptorSpec = [
        0 => ['pipe', 'r'],
        1 => ['pipe', 'w'],
        2 => ['pipe', 'w'],
    ];

    $process = proc_open($commandLine, $descriptorSpec, $pipes, __DIR__);
    if (!is_resource($process))
    {
        return [
            'job' => $job,
            'ok' => false,
            'exit_code' => 1,
            'output' => 'Failed to start sync process',
            'command' => $commandLine,
        ];
    }

    fclose($pipes[0]);
    $stdout = stream_get_contents($pipes[1]);
    fclose($pipes[1]);
    $stderr = stream_get_contents($pipes[2]);
    fclose($pipes[2]);

    $exitCode = proc_close($process);
    $output = trim($stdout . ($stderr ? "\n" . $stderr : ''));

    return [
        'job' => $job,
        'ok' => $exitCode === 0,
        'exit_code' => $exitCode,
        'output' => $output,
        'command' => $commandLine,
    ];
}

if (($_SERVER['REQUEST_METHOD'] ?? 'GET') !== 'POST')
{
    respond(['error' => 'Method not allowed'], 405);
}

$expectedToken = getenv('SYNC_CONTROL_TOKEN') ?: '';
if ($expectedToken === '')
{
    respond(['error' => 'SYNC_CONTROL_TOKEN is not configured'], 503);
}

$providedToken = $_SERVER['HTTP_X_SYNC_CONTROL_TOKEN'] ?? ($_POST['token'] ?? '');
if (!is_string($providedToken) || !hash_equals($expectedToken, $providedToken))
{
    respond(['error' => 'Forbidden'], 403);
}

$payload = load_payload();
$job = trim((string) ($payload['job'] ?? ''));
if ($job === '')
{
    respond(['error' => 'Job is required'], 400);
}

$runs = [];
$ok = true;
foreach (build_job_runs($job, $payload) as $run)
{
    $result = run_php_script($run['job'], $run['definition'], $payload);
    $runs[] = $result;
    if (!$result['ok'])
    {
        $ok = false;
        break;
    }
}

respond([
    'status' => $ok ? 'ok' : 'failed',
    'requested_job' => $job,
    'runs' => $runs,
], $ok ? 200 : 502);
