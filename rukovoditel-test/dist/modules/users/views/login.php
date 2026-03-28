<?php
/**
 * Этот файл является частью программы "CRM Руководитель" - конструктор CRM систем для бизнеса
 * https://www.rukovoditel.net.ru/
 * 
 * CRM Руководитель - это свободное программное обеспечение, 
 * распространяемое на условиях GNU GPLv3 https://www.gnu.org/licenses/gpl-3.0.html
 * 
 * Автор и правообладатель программы: Харчишина Ольга Александровна (RU), Харчишин Сергей Васильевич (RU).
 * Государственная регистрация программы для ЭВМ: 2023664624
 * https://fips.ru/EGD/3b18c104-1db7-4f2d-83fb-2d38e1474ca3
 */
?>

<?php
function docflow_login_env_value($key, $default = '')
{
    $value = getenv($key);

    if ($value === false)
    {
        return $default;
    }

    $value = trim((string) $value);
    return strlen($value) ? $value : $default;
}

$show_demo_login_modes = docflow_login_env_value('DOCFLOW_SHOW_DEMO_LOGIN_MODES', '0') === '1';
$login_modes = array(
    array(
        'title' => 'Администратор',
        'description' => 'Полный контур управления: настройки, роли, логи, интеграции и рабочие модули.',
        'eyebrow' => 'Админский режим',
        'username' => docflow_login_env_value('DOCFLOW_ADMIN_USERNAME', 'admin'),
        'password' => docflow_login_env_value('DOCFLOW_ADMIN_PASSWORD', 'admin123'),
    ),
    array(
        'title' => 'Пользователь',
        'description' => 'Чистый рабочий кабинет без техразделов: заявки, проекты, документы, база и МТЗ.',
        'eyebrow' => 'Пользовательский режим',
        'username' => docflow_login_env_value('DOCFLOW_EMPLOYEE_USERNAME', 'clinician.primary'),
        'password' => docflow_login_env_value('DOCFLOW_ROLE_DEFAULT_PASSWORD', 'rolepass123'),
    ),
);
?>

<div class="platform-login">
    <section class="platform-login-intro">
        <div class="platform-login-badge">Единая платформа документооборота</div>
        <h3 class="form-title"><?php echo ((!is_null(CFG_LOGIN_PAGE_HEADING) and strlen(CFG_LOGIN_PAGE_HEADING)) > 0 ? CFG_LOGIN_PAGE_HEADING : TEXT_HEADING_LOGIN) ?></h3>

        <?php echo ((!is_null(CFG_LOGIN_PAGE_CONTENT) and strlen(CFG_LOGIN_PAGE_CONTENT)) > 0 ? '<p class="platform-login-lead">' . CFG_LOGIN_PAGE_CONTENT . '</p>' : '<p class="platform-login-lead">Один вход в рабочий кабинет сотрудников, руководителей и канцелярии. Отсюда начинаются заявки, проекты, документы и официальный контур NauDoc.</p>') ?>

        <div class="login-modes">
            <?php foreach ($login_modes as $mode): ?>
                <div class="login-mode-card">
                    <div class="login-mode-eyebrow"><?php echo $mode['eyebrow'] ?></div>
                    <h4><?php echo $mode['title'] ?></h4>
                    <p><?php echo $mode['description'] ?></p>
                    <?php if($show_demo_login_modes): ?>
                        <div class="login-mode-credentials">
                            <span><?php echo $mode['username'] ?></span>
                            <span><?php echo $mode['password'] ?></span>
                        </div>
                        <button
                            type="button"
                            class="btn btn-default btn-sm login-mode-fill"
                            data-username="<?php echo $mode['username'] ?>"
                            data-password="<?php echo $mode['password'] ?>"
                        >Заполнить вход</button>
                    <?php else: ?>
                        <div class="login-mode-credentials">
                            <span>Используйте персональную учетную запись</span>
                        </div>
                    <?php endif; ?>
                </div>
            <?php endforeach; ?>
        </div>
    </section>

    <section class="platform-login-form-panel">
        <div class="platform-login-form-head">
            <div class="platform-login-form-kicker">Вход в систему</div>
            <h4>Начать работу</h4>
            <p><?php echo $show_demo_login_modes ? 'Введите свой логин или выберите один из двух подготовленных режимов.' : 'Введите персональные учетные данные, выданные администратором или корпоративным каталогом.' ?></p>
        </div>

        <?php echo maintenance_mode::login_message() ?>

<?php
//check if default login is enabled
if(CFG_ENABLE_SOCIAL_LOGIN != 2)
{
    echo form_tag('login_form', url_for('users/login', 'action=login'), array('class' => 'login-form'))
    ?>

    <div class="form-group">
        <!--ie8, ie9 does not support html5 placeholder, so we just show field title for that-->
        <label class="control-label visible-ie8 visible-ie9"><?php echo TEXT_USERNAME ?></label>
        <div class="input-icon">
            <i class="fa fa-user"></i>
            <input class="form-control placeholder-no-fix required" type="text" autocomplete="off" placeholder="<?php echo TEXT_USERNAME ?>" name="username" id="login-username"/>
        </div>
    </div>
    <div class="form-group">
        <label class="control-label visible-ie8 visible-ie9"><?php echo TEXT_PASSWORD ?></label>
        <div class="input-icon">
            <i class="fa fa-lock"></i>
            <input class="form-control placeholder-no-fix required"  type="password" autocomplete="off" placeholder="<?php echo TEXT_PASSWORD ?>" name="password" id="login-password"/>
        </div>
    </div>

        <?php if(app_recaptcha::is_enabled()): ?>
        <div class="form-group">
        <?php echo app_recaptcha::render() ?>	
        </div>
        <?php endif ?>

    <div class="form-actions">
        <div class="platform-login-actions">
            <button type="submit" class="btn btn-info platform-login-submit"><?php echo TEXT_BUTTON_LOGIN ?></button>

            <?php if(CFG_LOGIN_PAGE_HIDE_REMEMBER_ME != 1): ?>
                <label class="platform-login-remember"><?php echo input_checkbox_tag('remember_me', 1, array('checked' => (isset($_COOKIE['app_remember_me']) ? true : false))) ?><span><?php echo TEXT_REMEMBER_ME ?></span></label>
            <?php endif; ?>
        </div>
    </div>

    </form>

    <div class="forget-password platform-login-secondary-actions">
        <div class="platform-login-links">
            <a href="<?php echo url_for('users/restore_password') ?>"><?php echo TEXT_PASSWORD_FORGOTTEN ?></a>
            <?php if(CFG_USE_PUBLIC_REGISTRATION == 1) echo '<a class="platform-login-register" href="' . url_for('users/registration') . '">' . (strlen(CFG_REGISTRATION_BUTTON_TITLE) ? CFG_REGISTRATION_BUTTON_TITLE : TEXT_BUTTON_REGISTRATCION) . '</a>' ?>
        </div>
    </div>

<?php
}
?> 


<?php if(CFG_2STEP_VERIFICATION_ENABLED == 1 and CFG_LOGIN_BY_PHONE_NUMBER == 1 and CFG_2STEP_VERIFICATION_TYPE == 'sms'): ?>
    <div class="create-account platform-login-secondary-actions">
        <p><a href="<?php echo url_for('users/login_by_phone') ?>"><?php echo TEXT_LOGIN_BY_PHONE_NUMBER ?></a></p>
    </div>
<?php endif ?>

<?php if(strlen(CFG_LOGIN_DIGITAL_SIGNATURE_MODULE??'')): ?>
    <div class="create-account platform-login-secondary-actions">
        <p><a href="<?php echo url_for('users/signature_login') ?>"><?php echo TEXT_DIGITAL_SIGNATURE_LOGIN ?></a></p>
    </div>
<?php endif ?>


<?php if(CFG_LDAP_USE == 1): ?>
    <div class="create-account platform-login-secondary-actions">
        <p><a href="<?php echo url_for('users/ldap_login') ?>"><?php echo TEXT_MENU_LDAP_LOGIN ?></a></p>
    </div>
<?php endif ?>

<?php

if(guest_login::is_enabled())
{
    include(component_path('users/guest_login'));
}

//social login
if(CFG_ENABLE_SOCIAL_LOGIN != 0)
{
    include(component_path('users/social_login'));
}
?>
    </section>
</div>



<script>
    $(function ()
    {
        $('#login_form').validate();

        $('.login-mode-fill').on('click', function ()
        {
            $('#login-username').val($(this).data('username')).focus();
            $('#login-password').val($(this).data('password'));
        });
    });
</script> 



