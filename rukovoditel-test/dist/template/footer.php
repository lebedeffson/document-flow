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
$footer_html = app_copyright_text() . app_powered_by_text();
if(strlen(trim(strip_tags($footer_html))))
{
?>
<div class="footer noprint">
    <div class="footer-inner">
        <?= $footer_html ?>
    </div>
<div class="footer-tools">
	
</div>
</div>
<?php } ?>
