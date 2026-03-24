/*
 * FCKeditor - The text editor for internet
 * Copyright (C) 2003-2004 Frederico Caldeira Knabben
 * 
 * Licensed under the terms of the GNU Lesser General Public License:
 * 		http://www.opensource.org/licenses/lgpl-license.php
 * 
 * For further information visit:
 * 		http://www.fckeditor.net/
 * 
 * File Name: fck_1.js
 * 	This is the first part of the "FCK" object creation. This is the main
 * 	object that represents an editor instance.
 * 
 * Version:  2.0 RC3
 * Modified: 2005-02-27 21:46:32
 * 
 * File Authors:
 * 		Frederico Caldeira Knabben (fredck@fckeditor.net)
 */

FCK.Events	= new FCKEvents( FCK ) ;
FCK.Toolbar	= null ;

FCK.TempBaseTag = FCKConfig.BaseHref.length > 0 ? '<base href="' + FCKConfig.BaseHref + '" _fcktemp="true"></base>' : '' ;

FCK.StartEditor = function()
{
	// Get the editor's window and document (DOM)
	this.EditorWindow	= window.frames[ 'eEditorArea' ] ;
	this.EditorDocument	= this.EditorWindow.document ;

	// TODO: Wait stable version and remove the following commented lines.
	// The Base Path of the editor is saved to rebuild relative URL (IE issue).
//	this.BaseUrl = this.EditorDocument.location.protocol + '//' + this.EditorDocument.location.host ;

	if ( FCKBrowserInfo.IsGecko )
		this.MakeEditable() ;

	// Set the editor's startup contents
	this.SetHTML( FCKTools.GetLinkedFieldValue() ) ;

	// Attach the editor to the form onsubmit event
	FCKTools.AttachToLinkedFieldFormSubmit( this.UpdateLinkedField ) ;

	this.SetStatus( FCK_STATUS_ACTIVE ) ;
}

FCK.SetStatus = function( newStatus )
{
	this.Status = newStatus ;

	if ( newStatus == FCK_STATUS_ACTIVE )
	{
		// Force the focus in the window to go to the editor.
		window.onfocus = window.document.body.onfocus = FCK.Focus ;

		// Force the focus in the editor.
		if ( FCKConfig.StartupFocus )
			FCK.Focus() ;

		// @Packager.Compactor.Remove.Start
		var sBrowserSuffix = FCKBrowserInfo.IsIE ? "ie" : "gecko" ;

		FCKScriptLoader.AddScript( 'js/internals/fck_2.js' ) ;
		FCKScriptLoader.AddScript( 'js/internals/fck_2_' + sBrowserSuffix + '.js' ) ;
		FCKScriptLoader.AddScript( 'js/internals/fckselection.js' ) ;
		FCKScriptLoader.AddScript( 'js/internals/fckselection_' + sBrowserSuffix + '.js' ) ;
		FCKScriptLoader.AddScript( 'js/classes/fckpanel_' + sBrowserSuffix + '.js' ) ;
		FCKScriptLoader.AddScript( 'js/internals/fcktablehandler.js' ) ;
		FCKScriptLoader.AddScript( 'js/internals/fcktablehandler_' + sBrowserSuffix + '.js' ) ;
		FCKScriptLoader.AddScript( 'js/classes/fckxml_' + sBrowserSuffix + '.js' ) ;
		FCKScriptLoader.AddScript( 'js/classes/fckstyledef.js' ) ;
		FCKScriptLoader.AddScript( 'js/classes/fckstyledef_' + sBrowserSuffix + '.js' ) ;
		FCKScriptLoader.AddScript( 'js/classes/fckstylesloader.js' ) ;

		FCKScriptLoader.AddScript( 'js/commandclasses/fcknamedcommand.js' ) ;
		FCKScriptLoader.AddScript( 'js/commandclasses/fck_othercommands.js' ) ;
		FCKScriptLoader.AddScript( 'js/commandclasses/fckspellcheckcommand_' + sBrowserSuffix + '.js' ) ;
		FCKScriptLoader.AddScript( 'js/commandclasses/fcktextcolorcommand.js' ) ;
		FCKScriptLoader.AddScript( 'js/commandclasses/fckpasteplaintextcommand.js' ) ;
		FCKScriptLoader.AddScript( 'js/commandclasses/fckpastewordcommand.js' ) ;
		FCKScriptLoader.AddScript( 'js/commandclasses/fcktablecommand.js' ) ;
		FCKScriptLoader.AddScript( 'js/commandclasses/fckstylecommand.js' ) ;

		FCKScriptLoader.AddScript( 'js/internals/fckcommands.js' ) ;
		FCKScriptLoader.AddScript( 'js/classes/fcktoolbarbutton.js' ) ;
		FCKScriptLoader.AddScript( 'js/classes/fcktoolbarcombo.js' ) ;
		FCKScriptLoader.AddScript( 'js/classes/fckspecialcombo.js' ) ;
		FCKScriptLoader.AddScript( 'js/classes/fcktoolbarspecialcombo.js' ) ;
		FCKScriptLoader.AddScript( 'js/classes/fcktoolbarfontscombo.js' ) ;
		FCKScriptLoader.AddScript( 'js/classes/fcktoolbarfontsizecombo.js' ) ;
		FCKScriptLoader.AddScript( 'js/classes/fcktoolbarfontformatcombo.js' ) ;
		FCKScriptLoader.AddScript( 'js/classes/fcktoolbarstylecombo.js' ) ;
		FCKScriptLoader.AddScript( 'js/classes/fcktoolbarpanelbutton.js' ) ;
		FCKScriptLoader.AddScript( 'js/internals/fcktoolbaritems.js' ) ;
		FCKScriptLoader.AddScript( 'js/classes/fcktoolbar.js' ) ;
		FCKScriptLoader.AddScript( 'js/classes/fcktoolbarbreak_' + sBrowserSuffix + '.js' ) ;
		FCKScriptLoader.AddScript( 'js/internals/fcktoolbarset.js' ) ;
		FCKScriptLoader.AddScript( 'js/internals/fckdialog.js' ) ;
		FCKScriptLoader.AddScript( 'js/internals/fckdialog_' + sBrowserSuffix + '.js' ) ;
		FCKScriptLoader.AddScript( 'js/classes/fckcontextmenuitem.js' ) ;
		FCKScriptLoader.AddScript( 'js/classes/fckcontextmenuseparator.js' ) ;
		FCKScriptLoader.AddScript( 'js/classes/fckcontextmenugroup.js' ) ;
		FCKScriptLoader.AddScript( 'js/internals/fckcontextmenu.js' ) ;
		FCKScriptLoader.AddScript( 'js/internals/fckcontextmenu_' + sBrowserSuffix + '.js' ) ;
		FCKScriptLoader.AddScript( 'js/classes/fckplugin.js' ) ;
		FCKScriptLoader.AddScript( 'js/internals/fckplugins.js' ) ;
		FCKScriptLoader.AddScript( 'js/internals/fck_last.js' ) ;
		// @Packager.Compactor.Remove.End

		/* @Packager.Compactor.RemoveLine

		if ( FCKBrowserInfo.IsIE )
			FCKScriptLoader.AddScript( 'js/fckeditorcode_ie_2.js' ) ;
		else
			FCKScriptLoader.AddScript( 'js/fckeditorcode_gecko_2.js' ) ;

		@Packager.Compactor.RemoveLine */
	}

	this.Events.FireEvent( 'OnStatusChange', newStatus ) ;
	if ( this.OnStatusChange ) this.OnStatusChange( newStatus ) ;

}

FCK.GetHTML = function( format )
{
	var sHTML ;

	if ( FCK.EditMode == FCK_EDITMODE_WYSIWYG )
	{
		// TODO: Wait stable version and remove the following commented lines.
//		if ( FCKBrowserInfo.IsIE )
//			FCK.CheckRelativeLinks() ;

		if ( FCKBrowserInfo.IsIE )
			sHTML = this.EditorDocument.body.innerHTML.replace( FCKRegexLib.ToReplace, '$1' ) ;
		else
			sHTML = this.EditorDocument.body.innerHTML ;
	}
	else
		sHTML = document.getElementById('eSourceField').value ;

	if ( format )
		return FCKCodeFormatter.Format( sHTML ) ;
	else
		return sHTML ;
}

FCK.GetXHTML = function( format )
{
	var bSource = ( FCK.EditMode == FCK_EDITMODE_SOURCE ) ;

	if ( bSource )
		this.SwitchEditMode() ;

	// TODO: Wait stable version and remove the following commented lines.
//	if ( FCKBrowserInfo.IsIE )
//		FCK.CheckRelativeLinks() ;

	if ( FCKConfig.FullPage )
		var sXHTML = FCKXHtml.GetXHTML( this.EditorDocument.getElementsByTagName( 'html' )[0], true, format ) ;
	else
		var sXHTML = FCKXHtml.GetXHTML( this.EditorDocument.body, false, format ) ;

	if ( bSource )
		this.SwitchEditMode() ;

	if ( FCKBrowserInfo.IsIE )
		sXHTML = sXHTML.replace( FCKRegexLib.ToReplace, '$1' ) ;

	if ( FCK.DocTypeDeclaration && FCK.DocTypeDeclaration.length > 0 )
		sXHTML = FCK.DocTypeDeclaration + '\n' + sXHTML ;

	if ( FCK.XmlDeclaration && FCK.XmlDeclaration.length > 0 )
		sXHTML = FCK.XmlDeclaration + '\n' + sXHTML ;

	return sXHTML ;
}

FCK.UpdateLinkedField = function()
{
	if ( FCKConfig.EnableXHTML )
		FCKTools.SetLinkedFieldValue( FCK.GetXHTML( FCKConfig.FormatOutput ) ) ;
	else
		FCKTools.SetLinkedFieldValue( FCK.GetHTML( FCKConfig.FormatOutput ) ) ;
}

FCK.ShowContextMenu = function( x, y )
{
	if ( this.Status != FCK_STATUS_COMPLETE )
		return ;

	FCKContextMenu.Show( x, y ) ;
	this.Events.FireEvent( "OnContextMenu" ) ;
}

FCK.RegisteredDoubleClickHandlers = new Object() ;

FCK.OnDoubleClick = function( element )
{
	var oHandler = FCK.RegisteredDoubleClickHandlers[ element.tagName ] ;
	if ( oHandler )
	{
		oHandler( element ) ;
	}
}

// Register objects that can handle double click operations.
FCK.RegisterDoubleClickHandler = function( handlerFunction, tag )
{
	FCK.RegisteredDoubleClickHandlers[ tag.toUpperCase() ] = handlerFunction ;
}

