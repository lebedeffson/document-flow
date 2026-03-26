<?php

$service = $_GET['service'] ?? 'docspace';
$allowed_services = ['docspace', 'workspace'];

if(!in_array($service, $allowed_services))
{
    redirect_to('dashboard/page_not_found');
}

$titles = [
    'docspace' => 'ONLYOFFICE DocSpace',
    'workspace' => 'ONLYOFFICE Workspace',
];

$app_title = app_set_title($titles[$service]);
