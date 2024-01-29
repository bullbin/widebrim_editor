# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b3)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.richtext
import wx.aui
import wx.propgrid as pg

###########################################################################
## Class FirstRunWarning
###########################################################################

class FirstRunWarning ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Welcome to widebrim editor", pos = wx.DefaultPosition, size = wx.Size( 480,360 ), style = wx.CAPTION )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer16 = wx.BoxSizer( wx.VERTICAL )


		bSizer16.Add( ( 0, 5), 0, wx.EXPAND, 5 )

		self.m_staticText11 = wx.StaticText( self, wx.ID_ANY, u"widebrim editor License Agreement", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText11.Wrap( -1 )

		bSizer16.Add( self.m_staticText11, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL|wx.TOP, 10 )

		self.m_staticline11 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer16.Add( self.m_staticline11, 0, wx.EXPAND |wx.ALL, 5 )

		self.m_textCtrl12 = wx.TextCtrl( self, wx.ID_ANY, u"Thank you for your interest in the widebrim editor. Before using this application, please read our (\"our\", \"we\" : contributors to the widebrim project) EULA.\n\nwidebrim editor is a ROM (\"read-only memory\" : complete game executable format) editor for Professor Layton and the Diabolical Box. It was created through reverse engineering and has no endorsements by or connections to Nintendo, LEVEL-5 or the Professor Layton franchise. Use this tool respectfully when making fanworks.\n\nUsage of this tool may not be legal in your region depending on laws regarding ROM dumping and modification. Check your local legislation before using this tool. We do not condone any piracy - please dump your own cartridge for use with the editor.\n\nwidebrim editor does not make any modifications to the algorithmic content of the game. As such, some content produced from the editor will still be the derivative property of LEVEL-5 even if all Layton-related content is removed. Do not resell any works produced using by this tool. We will not assume any responsibilities for the legal repercussions of doing so.\n\nBy continuing, you declare that we are in no way responsible for any resulting action on works created by this tool.", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER|wx.TE_MULTILINE|wx.TE_READONLY )
		self.m_textCtrl12.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_BTNFACE ) )

		bSizer16.Add( self.m_textCtrl12, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )

		bSizer17 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer17.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.buttonDisagree = wx.Button( self, wx.ID_ANY, u"Disagree", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer17.Add( self.buttonDisagree, 0, wx.ALL, 5 )

		self.buttonAgree = wx.Button( self, wx.ID_ANY, u"Agree", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer17.Add( self.buttonAgree, 0, wx.ALL, 5 )


		bSizer16.Add( bSizer17, 0, wx.EXPAND, 5 )


		self.SetSizer( bSizer16 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.buttonDisagree.Bind( wx.EVT_BUTTON, self.buttonDisagreeOnButtonClick )
		self.buttonAgree.Bind( wx.EVT_BUTTON, self.buttonAgreeOnButtonClick )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def buttonDisagreeOnButtonClick( self, event ):
		event.Skip()

	def buttonAgreeOnButtonClick( self, event ):
		event.Skip()


###########################################################################
## Class StartupConfiguration
###########################################################################

class StartupConfiguration ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"widebrim editor Startup", pos = wx.DefaultPosition, size = wx.Size( 480,320 ), style = wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer49 = wx.BoxSizer( wx.VERTICAL )

		bSizer50 = wx.BoxSizer( wx.HORIZONTAL )

		self.btnSetupRom = wx.Button( self, wx.ID_ANY, u"   Change Filesystem ROM   ", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer50.Add( self.btnSetupRom, 0, wx.ALL, 5 )

		self.m_staticline12 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
		bSizer50.Add( self.m_staticline12, 0, wx.BOTTOM|wx.EXPAND|wx.RIGHT|wx.TOP, 5 )

		self.textRomName = wx.StaticText( self, wx.ID_ANY, u"No ROM loaded...", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.textRomName.Wrap( -1 )

		self.textRomName.Enable( False )

		bSizer50.Add( self.textRomName, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )


		bSizer49.Add( bSizer50, 0, wx.EXPAND, 5 )

		self.m_staticline13 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer49.Add( self.m_staticline13, 0, wx.EXPAND, 5 )

		gSizer2 = wx.GridSizer( 0, 2, 15, 15 )

		self.btnReopenLast = wx.Button( self, wx.ID_ANY, u"Reopen last edit...", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer2.Add( self.btnReopenLast, 0, wx.ALL|wx.EXPAND, 5 )

		self.btnOpenFolder = wx.Button( self, wx.ID_ANY, u"Load edit...", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer2.Add( self.btnOpenFolder, 0, wx.ALL|wx.EXPAND, 5 )

		self.btnCreateNew = wx.Button( self, wx.ID_ANY, u"Create edit from loaded ROM", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer2.Add( self.btnCreateNew, 0, wx.ALL|wx.EXPAND, 5 )

		self.btnCreateEmpty = wx.Button( self, wx.ID_ANY, u"Create edit from empty ROM", wx.DefaultPosition, wx.DefaultSize, 0 )
		gSizer2.Add( self.btnCreateEmpty, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer49.Add( gSizer2, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_staticline131 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer49.Add( self.m_staticline131, 0, wx.EXPAND, 2 )

		bSizer52 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer69 = wx.BoxSizer( wx.HORIZONTAL )

		self.reopenOnBoot = wx.CheckBox( self, wx.ID_ANY, u"Reopen last project on boot", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer69.Add( self.reopenOnBoot, 0, wx.ALL, 5 )


		bSizer69.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.useVfs = wx.CheckBox( self, wx.ID_ANY, u"Use virtual filesystem (VFS)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.useVfs.SetToolTip( u"The virtual filesystem is slower but aims to be safer for distributors and developers. Instead of distributing a ROM, a patch folder containing only changes is distributed.\n\nVFS works by expanding the ROM into another folder then tracking changes made to the ROM. It is non-destructive and makes no changes to the editing experience.\n\nWhen the mod is finished, the patch folder can be applied to create a ROM using the editor. If you do not enjoy the VFS workflow, you can apply the patch into a ROM and re-open the ROM without VFS enabled. This will apply all changes directly to the ROM.\n\nThe downsides to using a VFS is that file accesses are slower, so previews take longer to load. You must also be careful to not create copyrighted assets inside the VFS, e.g., by importing assets from the game back into itself. Finally, there is no guarantee that mods made in this fashion will contain no copyrighted content, so be aware of any dangers before distributing patch folders." )

		bSizer69.Add( self.useVfs, 0, wx.ALL, 5 )


		bSizer52.Add( bSizer69, 1, wx.EXPAND, 5 )


		bSizer49.Add( bSizer52, 0, wx.EXPAND, 5 )


		self.SetSizer( bSizer49 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.btnSetupRom.Bind( wx.EVT_BUTTON, self.btnSetupRomOnButtonClick )
		self.btnReopenLast.Bind( wx.EVT_BUTTON, self.btnReopenLastOnButtonClick )
		self.btnOpenFolder.Bind( wx.EVT_BUTTON, self.btnOpenFolderOnButtonClick )
		self.btnCreateNew.Bind( wx.EVT_BUTTON, self.btnCreateNewOnButtonClick )
		self.btnCreateEmpty.Bind( wx.EVT_BUTTON, self.btnCreateEmptyOnButtonClick )
		self.reopenOnBoot.Bind( wx.EVT_CHECKBOX, self.reopenOnBootOnCheckBox )
		self.useVfs.Bind( wx.EVT_CHECKBOX, self.useVfsOnCheckBox )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def btnSetupRomOnButtonClick( self, event ):
		event.Skip()

	def btnReopenLastOnButtonClick( self, event ):
		event.Skip()

	def btnOpenFolderOnButtonClick( self, event ):
		event.Skip()

	def btnCreateNewOnButtonClick( self, event ):
		event.Skip()

	def btnCreateEmptyOnButtonClick( self, event ):
		event.Skip()

	def reopenOnBootOnCheckBox( self, event ):
		event.Skip()

	def useVfsOnCheckBox( self, event ):
		event.Skip()


###########################################################################
## Class PickerBgx
###########################################################################

class PickerBgx ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Replace Background", pos = wx.DefaultPosition, size = wx.Size( 640,540 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.Size( 640,540 ), wx.DefaultSize )

		bSizer65 = wx.BoxSizer( wx.VERTICAL )

		bSizer86 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer75 = wx.BoxSizer( wx.VERTICAL )

		self.searchFilesystem = wx.SearchCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.searchFilesystem.ShowSearchButton( True )
		self.searchFilesystem.ShowCancelButton( False )
		bSizer75.Add( self.searchFilesystem, 0, wx.ALL|wx.EXPAND, 5 )

		self.treeFilesystem = wx.TreeCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_DEFAULT_STYLE )
		bSizer75.Add( self.treeFilesystem, 4, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )


		bSizer86.Add( bSizer75, 1, wx.EXPAND, 5 )

		bSizer87 = wx.BoxSizer( wx.VERTICAL )

		bSizer72 = wx.BoxSizer( wx.VERTICAL )


		bSizer72.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		sbSizer26 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Preview (selected)" ), wx.VERTICAL )

		self.bitmapPreviewBackground = wx.StaticBitmap( sbSizer26.GetStaticBox(), wx.ID_ANY, wx.NullBitmap, wx.Point( 256,192 ), wx.DefaultSize, 0 )
		self.bitmapPreviewBackground.SetMinSize( wx.Size( 256,192 ) )
		self.bitmapPreviewBackground.SetMaxSize( wx.Size( 256,192 ) )

		sbSizer26.Add( self.bitmapPreviewBackground, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.LEFT|wx.RIGHT|wx.TOP, 5 )

		bSizer73 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer73.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.btnConfirmSelected = wx.Button( sbSizer26.GetStaticBox(), wx.ID_ANY, u"Use selected image", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer73.Add( self.btnConfirmSelected, 5, wx.ALL|wx.EXPAND, 5 )


		bSizer73.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		sbSizer26.Add( bSizer73, 1, wx.EXPAND, 5 )


		bSizer72.Add( sbSizer26, 0, wx.EXPAND, 5 )

		sbSizer27 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Custom Image" ), wx.VERTICAL )

		bSizer74 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer74.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		bSizer70 = wx.BoxSizer( wx.VERTICAL )

		self.btnImportImage = wx.Button( sbSizer27.GetStaticBox(), wx.ID_ANY, u"Import new image into folder...", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer70.Add( self.btnImportImage, 0, wx.ALL|wx.EXPAND, 5 )

		self.btnAddFolder = wx.Button( sbSizer27.GetStaticBox(), wx.ID_ANY, u"Add new folder...", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer70.Add( self.btnAddFolder, 0, wx.ALL|wx.EXPAND, 5 )

		self.btnDeleteFolder = wx.Button( sbSizer27.GetStaticBox(), wx.ID_ANY, u"Delete selected folder...", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer70.Add( self.btnDeleteFolder, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer74.Add( bSizer70, 6, wx.EXPAND, 5 )


		bSizer74.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		sbSizer27.Add( bSizer74, 1, wx.EXPAND, 5 )

		self.m_staticText49 = wx.StaticText( sbSizer27.GetStaticBox(), wx.ID_ANY, u"Use the Asset Manager for file management.", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText49.Wrap( -1 )

		self.m_staticText49.Enable( False )

		sbSizer27.Add( self.m_staticText49, 0, wx.ALIGN_CENTER|wx.ALL, 5 )


		bSizer72.Add( sbSizer27, 1, wx.EXPAND, 5 )


		bSizer72.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		bSizer87.Add( bSizer72, 1, wx.EXPAND, 5 )


		bSizer86.Add( bSizer87, 0, wx.EXPAND, 5 )


		bSizer65.Add( bSizer86, 1, wx.EXPAND, 5 )

		self.m_staticline17 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer65.Add( self.m_staticline17, 0, wx.EXPAND, 5 )

		bSizer67 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer67.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_staticText45 = wx.StaticText( self, wx.ID_ANY, u"Confirm using controls above", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText45.Wrap( -1 )

		self.m_staticText45.Enable( False )

		bSizer67.Add( self.m_staticText45, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.btnRemoveImage = wx.Button( self, wx.ID_ANY, u"Use hidden image", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer67.Add( self.btnRemoveImage, 0, wx.ALL, 5 )

		self.btnCancel = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer67.Add( self.btnCancel, 0, wx.ALL, 5 )


		bSizer65.Add( bSizer67, 0, wx.EXPAND, 5 )


		self.SetSizer( bSizer65 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.treeFilesystem.Bind( wx.EVT_TREE_ITEM_ACTIVATED, self.treeFilesystemOnTreeItemActivated )
		self.btnConfirmSelected.Bind( wx.EVT_BUTTON, self.btnConfirmSelectedOnButtonClick )
		self.btnImportImage.Bind( wx.EVT_BUTTON, self.btnImportImageOnButtonClick )
		self.btnAddFolder.Bind( wx.EVT_BUTTON, self.btnAddFolderOnButtonClick )
		self.btnDeleteFolder.Bind( wx.EVT_BUTTON, self.btnDeleteFolderOnButtonClick )
		self.btnRemoveImage.Bind( wx.EVT_BUTTON, self.btnRemoveImageOnButtonClick )
		self.btnCancel.Bind( wx.EVT_BUTTON, self.btnCancelOnButtonClick )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def treeFilesystemOnTreeItemActivated( self, event ):
		event.Skip()

	def btnConfirmSelectedOnButtonClick( self, event ):
		event.Skip()

	def btnImportImageOnButtonClick( self, event ):
		event.Skip()

	def btnAddFolderOnButtonClick( self, event ):
		event.Skip()

	def btnDeleteFolderOnButtonClick( self, event ):
		event.Skip()

	def btnRemoveImageOnButtonClick( self, event ):
		event.Skip()

	def btnCancelOnButtonClick( self, event ):
		event.Skip()


###########################################################################
## Class PickerRemapAnim
###########################################################################

class PickerRemapAnim ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Remap Animation", pos = wx.DefaultPosition, size = wx.Size( 600,400 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.Size( 600,400 ), wx.DefaultSize )

		bSizer65 = wx.BoxSizer( wx.VERTICAL )

		bSizer86 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer86.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		bSizer87 = wx.BoxSizer( wx.HORIZONTAL )

		sbSizer261 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Source Animation" ), wx.VERTICAL )

		self.bitmapSourceAnim = wx.StaticBitmap( sbSizer261.GetStaticBox(), wx.ID_ANY, wx.NullBitmap, wx.Point( 256,192 ), wx.DefaultSize, 0 )
		self.bitmapSourceAnim.SetMinSize( wx.Size( 256,192 ) )
		self.bitmapSourceAnim.SetMaxSize( wx.Size( 256,192 ) )

		sbSizer261.Add( self.bitmapSourceAnim, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )

		listboxSourceAnimChoices = [ u"Animation 1", u"Animation 2", u"Animation 3", u"Animation 4", u"Animation 5" ]
		self.listboxSourceAnim = wx.ListBox( sbSizer261.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, listboxSourceAnimChoices, 0 )
		sbSizer261.Add( self.listboxSourceAnim, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer87.Add( sbSizer261, 1, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.m_staticText55 = wx.StaticText( self, wx.ID_ANY, u"to", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText55.Wrap( -1 )

		bSizer87.Add( self.m_staticText55, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		sbSizer26 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Destination Animation" ), wx.VERTICAL )

		self.bitmapDestinationAnim = wx.StaticBitmap( sbSizer26.GetStaticBox(), wx.ID_ANY, wx.NullBitmap, wx.Point( 256,192 ), wx.DefaultSize, 0 )
		self.bitmapDestinationAnim.SetMinSize( wx.Size( 256,192 ) )
		self.bitmapDestinationAnim.SetMaxSize( wx.Size( 256,192 ) )

		sbSizer26.Add( self.bitmapDestinationAnim, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )

		choiceDestinationAnimChoices = []
		self.choiceDestinationAnim = wx.Choice( sbSizer26.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choiceDestinationAnimChoices, 0 )
		self.choiceDestinationAnim.SetSelection( 0 )
		sbSizer26.Add( self.choiceDestinationAnim, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer87.Add( sbSizer26, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		bSizer86.Add( bSizer87, 0, wx.EXPAND, 5 )


		bSizer86.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		bSizer65.Add( bSizer86, 1, wx.EXPAND, 5 )

		self.m_staticline17 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer65.Add( self.m_staticline17, 0, wx.EXPAND, 5 )

		bSizer67 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer67.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_staticText45 = wx.StaticText( self, wx.ID_ANY, u"Confirmation available once all entries have been remapped", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText45.Wrap( -1 )

		self.m_staticText45.Enable( False )

		bSizer67.Add( self.m_staticText45, 0, wx.ALIGN_CENTER|wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		self.btnConfirm = wx.Button( self, wx.ID_ANY, u"Mapping incomplete", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.btnConfirm.Enable( False )

		bSizer67.Add( self.btnConfirm, 0, wx.ALL, 5 )

		self.btnCancel = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer67.Add( self.btnCancel, 0, wx.ALL, 5 )


		bSizer65.Add( bSizer67, 0, wx.EXPAND, 5 )


		self.SetSizer( bSizer65 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.listboxSourceAnim.Bind( wx.EVT_LISTBOX, self.listboxSourceAnimOnListBox )
		self.choiceDestinationAnim.Bind( wx.EVT_CHOICE, self.choiceDestinationAnimOnChoice )
		self.btnConfirm.Bind( wx.EVT_BUTTON, self.btnConfirmOnButtonClick )
		self.btnCancel.Bind( wx.EVT_BUTTON, self.btnCancelOnButtonClick )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def listboxSourceAnimOnListBox( self, event ):
		event.Skip()

	def choiceDestinationAnimOnChoice( self, event ):
		event.Skip()

	def btnConfirmOnButtonClick( self, event ):
		event.Skip()

	def btnCancelOnButtonClick( self, event ):
		event.Skip()


###########################################################################
## Class PickerEvent
###########################################################################

class PickerEvent ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Change Event", pos = wx.DefaultPosition, size = wx.Size( 854,540 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.Size( 854,540 ), wx.DefaultSize )

		bSizer65 = wx.BoxSizer( wx.VERTICAL )

		bSizer86 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer75 = wx.BoxSizer( wx.VERTICAL )

		self.searchEvent = wx.SearchCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.searchEvent.ShowSearchButton( True )
		self.searchEvent.ShowCancelButton( False )
		bSizer75.Add( self.searchEvent, 0, wx.ALL|wx.EXPAND, 5 )

		self.treeEvent = wx.TreeCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT )
		bSizer75.Add( self.treeEvent, 4, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )


		bSizer86.Add( bSizer75, 1, wx.EXPAND, 5 )

		bSizer87 = wx.BoxSizer( wx.VERTICAL )

		bSizer72 = wx.BoxSizer( wx.VERTICAL )


		bSizer72.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		sbSizer26 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Preview (selected)" ), wx.VERTICAL )

		self.bitmapPreviewTopScreen = wx.StaticBitmap( sbSizer26.GetStaticBox(), wx.ID_ANY, wx.NullBitmap, wx.Point( 256,192 ), wx.DefaultSize, 0 )
		self.bitmapPreviewTopScreen.SetMinSize( wx.Size( 256,192 ) )
		self.bitmapPreviewTopScreen.SetMaxSize( wx.Size( 256,192 ) )

		sbSizer26.Add( self.bitmapPreviewTopScreen, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.LEFT|wx.RIGHT|wx.TOP, 5 )

		self.bitmapPreviewBottomScreen = wx.StaticBitmap( sbSizer26.GetStaticBox(), wx.ID_ANY, wx.NullBitmap, wx.Point( 256,192 ), wx.DefaultSize, 0 )
		self.bitmapPreviewBottomScreen.SetMinSize( wx.Size( 256,192 ) )
		self.bitmapPreviewBottomScreen.SetMaxSize( wx.Size( 256,192 ) )

		sbSizer26.Add( self.bitmapPreviewBottomScreen, 0, wx.ALL, 5 )

		bSizer73 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer73.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.btnConfirmSelected = wx.Button( sbSizer26.GetStaticBox(), wx.ID_ANY, u"Use selected event", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer73.Add( self.btnConfirmSelected, 5, wx.ALL|wx.EXPAND, 5 )


		bSizer73.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		sbSizer26.Add( bSizer73, 1, wx.EXPAND, 5 )


		bSizer72.Add( sbSizer26, 0, wx.EXPAND, 5 )


		bSizer72.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		bSizer87.Add( bSizer72, 1, wx.EXPAND, 5 )


		bSizer86.Add( bSizer87, 0, wx.EXPAND, 5 )


		bSizer65.Add( bSizer86, 1, wx.EXPAND, 5 )

		self.m_staticline17 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer65.Add( self.m_staticline17, 0, wx.EXPAND, 5 )

		bSizer67 = wx.BoxSizer( wx.HORIZONTAL )

		self.checkConditionalWarning = wx.CheckBox( self, wx.ID_ANY, u"Warn against potentially buggy choices", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkConditionalWarning.SetValue(True)
		self.checkConditionalWarning.SetToolTip( u"Enabling this setting will cause a warning to appear when any 'unsafe' events are picked. These won't be previewed unless the warning is dismissed.\n\nAn unsafe event is an event in which jumping to it could cause gameplay to end in an unintended state. This includes anything conditional - the game won't follow branching as intended if anything but the base (topmost) event is chosen.\n\nThis setting can be safely disabled if you know the consequences of jumping to the event being picked." )

		bSizer67.Add( self.checkConditionalWarning, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		bSizer67.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_staticText45 = wx.StaticText( self, wx.ID_ANY, u"Confirm using button above", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText45.Wrap( -1 )

		self.m_staticText45.Enable( False )

		bSizer67.Add( self.m_staticText45, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.btnCancel = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer67.Add( self.btnCancel, 0, wx.ALL, 5 )


		bSizer65.Add( bSizer67, 0, wx.EXPAND, 5 )


		self.SetSizer( bSizer65 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.treeEvent.Bind( wx.EVT_TREE_ITEM_ACTIVATED, self.treeFilesystemOnTreeItemActivated )
		self.treeEvent.Bind( wx.EVT_TREE_SEL_CHANGED, self.treeEventOnTreeSelChanged )
		self.btnConfirmSelected.Bind( wx.EVT_BUTTON, self.btnConfirmSelectedOnButtonClick )
		self.btnCancel.Bind( wx.EVT_BUTTON, self.btnCancelOnButtonClick )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def treeFilesystemOnTreeItemActivated( self, event ):
		event.Skip()

	def treeEventOnTreeSelChanged( self, event ):
		event.Skip()

	def btnConfirmSelectedOnButtonClick( self, event ):
		event.Skip()

	def btnCancelOnButtonClick( self, event ):
		event.Skip()


###########################################################################
## Class PickerNode
###########################################################################

class PickerNode ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Generic Node Picker", pos = wx.DefaultPosition, size = wx.Size( 854,540 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.Size( 854,540 ), wx.DefaultSize )

		bSizer65 = wx.BoxSizer( wx.VERTICAL )

		bSizer86 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer75 = wx.BoxSizer( wx.VERTICAL )

		self.searchData = wx.SearchCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.searchData.ShowSearchButton( True )
		self.searchData.ShowCancelButton( False )
		bSizer75.Add( self.searchData, 0, wx.ALL|wx.EXPAND, 5 )

		self.treeData = wx.TreeCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT )
		bSizer75.Add( self.treeData, 4, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )


		bSizer86.Add( bSizer75, 1, wx.EXPAND, 5 )

		bSizer87 = wx.BoxSizer( wx.VERTICAL )

		bSizer72 = wx.BoxSizer( wx.VERTICAL )


		bSizer72.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		sbSizer26 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Confirm Selection" ), wx.VERTICAL )

		sbSizer26.SetMinSize( wx.Size( 256,-1 ) )
		self.textActiveSelection = wx.StaticText( sbSizer26.GetStaticBox(), wx.ID_ANY, u"Nothing selected", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.textActiveSelection.Wrap( -1 )

		self.textActiveSelection.Enable( False )

		sbSizer26.Add( self.textActiveSelection, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

		bSizer73 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer73.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.btnConfirmSelected = wx.Button( sbSizer26.GetStaticBox(), wx.ID_ANY, u"Confirm", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer73.Add( self.btnConfirmSelected, 5, wx.ALL|wx.EXPAND, 5 )


		bSizer73.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		sbSizer26.Add( bSizer73, 1, wx.EXPAND, 5 )


		bSizer72.Add( sbSizer26, 0, wx.EXPAND, 5 )


		bSizer72.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		bSizer87.Add( bSizer72, 1, wx.EXPAND, 5 )


		bSizer86.Add( bSizer87, 0, wx.EXPAND, 5 )


		bSizer65.Add( bSizer86, 1, wx.EXPAND, 5 )

		self.m_staticline17 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer65.Add( self.m_staticline17, 0, wx.EXPAND, 5 )

		bSizer67 = wx.BoxSizer( wx.HORIZONTAL )

		self.checkSafety = wx.CheckBox( self, wx.ID_ANY, u"Warn against potentially buggy choices", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkSafety.SetValue(True)
		self.checkSafety.SetToolTip( u"Enabling this setting will cause a warning to appear when any 'unsafe' events are picked. These won't be previewed unless the warning is dismissed.\n\nAn unsafe event is an event in which jumping to it could cause gameplay to end in an unintended state. This includes anything conditional - the game won't follow branching as intended if anything but the base (topmost) event is chosen.\n\nThis setting can be safely disabled if you know the consequences of jumping to the event being picked." )

		bSizer67.Add( self.checkSafety, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		bSizer67.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_staticText45 = wx.StaticText( self, wx.ID_ANY, u"Confirm using button above", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText45.Wrap( -1 )

		self.m_staticText45.Enable( False )

		bSizer67.Add( self.m_staticText45, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.btnCancel = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer67.Add( self.btnCancel, 0, wx.ALL, 5 )


		bSizer65.Add( bSizer67, 0, wx.EXPAND, 5 )


		self.SetSizer( bSizer65 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.treeData.Bind( wx.EVT_TREE_ITEM_ACTIVATED, self.treeDataOnTreeItemActivated )
		self.treeData.Bind( wx.EVT_TREE_SEL_CHANGED, self.treeDataOnTreeSelChanged )
		self.btnConfirmSelected.Bind( wx.EVT_BUTTON, self.btnConfirmSelectedOnButtonClick )
		self.checkSafety.Bind( wx.EVT_CHECKBOX, self.checkSafetyOnCheckBox )
		self.btnCancel.Bind( wx.EVT_BUTTON, self.btnCancelOnButtonClick )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def treeDataOnTreeItemActivated( self, event ):
		event.Skip()

	def treeDataOnTreeSelChanged( self, event ):
		event.Skip()

	def btnConfirmSelectedOnButtonClick( self, event ):
		event.Skip()

	def checkSafetyOnCheckBox( self, event ):
		event.Skip()

	def btnCancelOnButtonClick( self, event ):
		event.Skip()


###########################################################################
## Class PickerMultipleChoice
###########################################################################

class PickerMultipleChoice ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Choose Operand Value", pos = wx.DefaultPosition, size = wx.Size( 640,272 ), style = wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.Size( 640,272 ), wx.DefaultSize )

		bSizer65 = wx.BoxSizer( wx.VERTICAL )

		bSizer105 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer107 = wx.BoxSizer( wx.VERTICAL )


		bSizer107.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_staticText54 = wx.StaticText( self, wx.ID_ANY, u"Choice", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText54.Wrap( -1 )

		self.m_staticText54.Enable( False )

		bSizer107.Add( self.m_staticText54, 0, wx.ALL, 5 )

		choiceOperandChoices = []
		self.choiceOperand = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choiceOperandChoices, 0 )
		self.choiceOperand.SetSelection( 0 )
		bSizer107.Add( self.choiceOperand, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )


		bSizer107.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		bSizer105.Add( bSizer107, 1, wx.EXPAND, 5 )

		self.m_staticline28 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
		bSizer105.Add( self.m_staticline28, 0, wx.EXPAND |wx.ALL, 5 )

		bSizer106 = wx.BoxSizer( wx.VERTICAL )


		bSizer106.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_staticText53 = wx.StaticText( self, wx.ID_ANY, u"Description", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText53.Wrap( -1 )

		self.m_staticText53.Enable( False )

		bSizer106.Add( self.m_staticText53, 0, wx.ALL, 5 )

		self.textOperandDescription = wx.TextCtrl( self, wx.ID_ANY, u"test0\ntest1\ntest2\ntest3", wx.DefaultPosition, wx.DefaultSize, wx.TE_BESTWRAP|wx.TE_MULTILINE|wx.TE_READONLY|wx.BORDER_NONE )
		self.textOperandDescription.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_MENU ) )

		bSizer106.Add( self.textOperandDescription, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )


		bSizer106.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		bSizer105.Add( bSizer106, 2, wx.EXPAND, 5 )


		bSizer65.Add( bSizer105, 1, wx.EXPAND, 5 )

		self.m_staticline17 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer65.Add( self.m_staticline17, 0, wx.EXPAND, 5 )

		bSizer67 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer67.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.btnAgree = wx.Button( self, wx.ID_ANY, u"Confirm", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer67.Add( self.btnAgree, 0, wx.ALL, 5 )

		self.btnCancel = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer67.Add( self.btnCancel, 0, wx.ALL, 5 )


		bSizer65.Add( bSizer67, 0, wx.EXPAND, 5 )


		self.SetSizer( bSizer65 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.choiceOperand.Bind( wx.EVT_CHOICE, self.choiceOperandOnChoice )
		self.btnAgree.Bind( wx.EVT_BUTTON, self.btnAgreeOnButtonClick )
		self.btnCancel.Bind( wx.EVT_BUTTON, self.btnCancelOnButtonClick )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def choiceOperandOnChoice( self, event ):
		event.Skip()

	def btnAgreeOnButtonClick( self, event ):
		event.Skip()

	def btnCancelOnButtonClick( self, event ):
		event.Skip()


###########################################################################
## Class PickerChangeBoundary
###########################################################################

class PickerChangeBoundary ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Edit Boundary", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer79 = wx.BoxSizer( wx.VERTICAL )

		self.panelBitmap = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 512,384 ), wx.TAB_TRAVERSAL )
		bSizer79.Add( self.panelBitmap, 0, wx.EXPAND |wx.ALL, 5 )

		self.m_staticline22 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer79.Add( self.m_staticline22, 0, wx.EXPAND, 5 )

		bSizer67 = wx.BoxSizer( wx.HORIZONTAL )

		self.btnReset = wx.Button( self, wx.ID_ANY, u"Reset", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer67.Add( self.btnReset, 0, wx.ALL, 5 )

		self.btnCreateMidSize = wx.Button( self, wx.ID_ANY, u"Fit to midscreen", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer67.Add( self.btnCreateMidSize, 0, wx.ALL, 5 )

		self.btnSetBoundaryFromAnim = wx.Button( self, wx.ID_ANY, u"Fit to animation", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer67.Add( self.btnSetBoundaryFromAnim, 0, wx.ALL, 5 )


		bSizer67.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.btnAgree = wx.Button( self, wx.ID_ANY, u"Confirm", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer67.Add( self.btnAgree, 0, wx.ALL, 5 )

		self.btnCancel = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer67.Add( self.btnCancel, 0, wx.ALL, 5 )


		bSizer79.Add( bSizer67, 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer79 )
		self.Layout()
		bSizer79.Fit( self )

		self.Centre( wx.BOTH )

		# Connect Events
		self.Bind( wx.EVT_PAINT, self.PickerChangeBoundaryOnPaint )
		self.panelBitmap.Bind( wx.EVT_LEFT_DOWN, self.panelBitmapOnLeftDown )
		self.panelBitmap.Bind( wx.EVT_LEFT_UP, self.panelBitmapOnLeftUp )
		self.panelBitmap.Bind( wx.EVT_MOTION, self.panelBitmapOnMotion )
		self.panelBitmap.Bind( wx.EVT_PAINT, self.panelBitmapOnPaint )
		self.btnReset.Bind( wx.EVT_BUTTON, self.btnResetOnButtonClick )
		self.btnCreateMidSize.Bind( wx.EVT_BUTTON, self.btnCreateMidSizeOnButtonClick )
		self.btnSetBoundaryFromAnim.Bind( wx.EVT_BUTTON, self.btnSetBoundaryFromAnimOnButtonClick )
		self.btnAgree.Bind( wx.EVT_BUTTON, self.btnAgreeOnButtonClick )
		self.btnCancel.Bind( wx.EVT_BUTTON, self.btnCancelOnButtonClick )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def PickerChangeBoundaryOnPaint( self, event ):
		event.Skip()

	def panelBitmapOnLeftDown( self, event ):
		event.Skip()

	def panelBitmapOnLeftUp( self, event ):
		event.Skip()

	def panelBitmapOnMotion( self, event ):
		event.Skip()

	def panelBitmapOnPaint( self, event ):
		event.Skip()

	def btnResetOnButtonClick( self, event ):
		event.Skip()

	def btnCreateMidSizeOnButtonClick( self, event ):
		event.Skip()

	def btnSetBoundaryFromAnimOnButtonClick( self, event ):
		event.Skip()

	def btnAgreeOnButtonClick( self, event ):
		event.Skip()

	def btnCancelOnButtonClick( self, event ):
		event.Skip()


###########################################################################
## Class EditTalkscript
###########################################################################

class EditTalkscript ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Edit TalkScript", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		bSizer106 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_scrolledWindow3 = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( 480,360 ), wx.HSCROLL|wx.VSCROLL )
		self.m_scrolledWindow3.SetScrollRate( 5, 5 )
		bSizer107 = wx.BoxSizer( wx.VERTICAL )

		self.textCtrlTalkscript = wx.TextCtrl( self.m_scrolledWindow3, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( -1,-1 ), wx.TE_MULTILINE )
		bSizer107.Add( self.textCtrlTalkscript, 1, wx.ALL|wx.EXPAND, 5 )


		self.m_scrolledWindow3.SetSizer( bSizer107 )
		self.m_scrolledWindow3.Layout()
		bSizer106.Add( self.m_scrolledWindow3, 1, wx.EXPAND |wx.ALL, 5 )

		self.m_staticline30 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
		bSizer106.Add( self.m_staticline30, 0, wx.EXPAND |wx.ALL, 5 )

		bSizer108 = wx.BoxSizer( wx.VERTICAL )


		bSizer108.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		sbSizer36 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Options" ), wx.VERTICAL )

		self.btnApplyWrap = wx.Button( sbSizer36.GetStaticBox(), wx.ID_ANY, u"Run line wrapper", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer36.Add( self.btnApplyWrap, 0, wx.ALL, 5 )


		bSizer108.Add( sbSizer36, 0, wx.EXPAND, 5 )


		bSizer108.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		sbSizer35 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Text Rendering Preview" ), wx.VERTICAL )

		self.bitmapPreview = wx.StaticBitmap( sbSizer35.GetStaticBox(), wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 256,192 ), 0 )
		sbSizer35.Add( self.bitmapPreview, 0, wx.ALL, 5 )


		bSizer108.Add( sbSizer35, 0, 0, 5 )

		bSizer109 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer109.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.btnConfirm = wx.Button( self, wx.ID_ANY, u"Confirm", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer109.Add( self.btnConfirm, 0, wx.ALL, 5 )

		self.btnCancel = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer109.Add( self.btnCancel, 0, wx.ALL, 5 )


		bSizer108.Add( bSizer109, 0, wx.EXPAND, 5 )


		bSizer108.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		bSizer106.Add( bSizer108, 0, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( bSizer106 )
		self.Layout()
		bSizer106.Fit( self )

		self.Centre( wx.BOTH )

		# Connect Events
		self.textCtrlTalkscript.Bind( wx.EVT_TEXT, self.textCtrlTalkscriptOnText )
		self.btnApplyWrap.Bind( wx.EVT_BUTTON, self.btnApplyWrapOnButtonClick )
		self.btnConfirm.Bind( wx.EVT_BUTTON, self.btnConfirmOnButtonClick )
		self.btnCancel.Bind( wx.EVT_BUTTON, self.btnCancelOnButtonClick )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def textCtrlTalkscriptOnText( self, event ):
		event.Skip()

	def btnApplyWrapOnButtonClick( self, event ):
		event.Skip()

	def btnConfirmOnButtonClick( self, event ):
		event.Skip()

	def btnCancelOnButtonClick( self, event ):
		event.Skip()


###########################################################################
## Class EditTalkscriptRich
###########################################################################

class EditTalkscriptRich ( wx.Dialog ):

	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Edit TalkScript", pos = wx.DefaultPosition, size = wx.Size( 960,480 ), style = wx.DEFAULT_DIALOG_STYLE|wx.MAXIMIZE_BOX|wx.MINIMIZE_BOX|wx.RESIZE_BORDER )

		self.SetSizeHints( wx.Size( 960,480 ), wx.DefaultSize )

		bSizer106 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer1091 = wx.BoxSizer( wx.VERTICAL )

		bSizer110 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer114 = wx.BoxSizer( wx.VERTICAL )

		self.m_staticText54 = wx.StaticText( self, wx.ID_ANY, u"Colors", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText54.Wrap( -1 )

		self.m_staticText54.Enable( False )

		bSizer114.Add( self.m_staticText54, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.TOP|wx.RIGHT|wx.LEFT, 5 )

		bSizer112 = wx.BoxSizer( wx.HORIZONTAL )

		self.btnColorBlack = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
		bSizer112.Add( self.btnColorBlack, 0, wx.ALL, 5 )

		self.btnColorWhite = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
		bSizer112.Add( self.btnColorWhite, 0, wx.ALL, 5 )

		self.btnColorRed = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
		bSizer112.Add( self.btnColorRed, 0, wx.ALL, 5 )

		self.btnColorGreen = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
		bSizer112.Add( self.btnColorGreen, 0, wx.ALL, 5 )


		bSizer114.Add( bSizer112, 0, wx.EXPAND, 5 )


		bSizer110.Add( bSizer114, 0, wx.EXPAND, 5 )

		self.m_staticline31 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
		bSizer110.Add( self.m_staticline31, 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 5 )

		bSizer113 = wx.BoxSizer( wx.VERTICAL )

		self.m_staticText53 = wx.StaticText( self, wx.ID_ANY, u"Commands", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText53.Wrap( -1 )

		self.m_staticText53.Enable( False )

		bSizer113.Add( self.m_staticText53, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.TOP|wx.RIGHT|wx.LEFT, 5 )

		bSizer111 = wx.BoxSizer( wx.HORIZONTAL )

		self.btnCmdAnim = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
		self.btnCmdAnim.SetToolTip( u"Change animation" )

		bSizer111.Add( self.btnCmdAnim, 0, wx.ALL, 5 )

		self.btnCmdDelay = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
		self.btnCmdDelay.SetToolTip( u"Add delay" )

		bSizer111.Add( self.btnCmdDelay, 0, wx.ALL, 5 )

		self.btnCmdPause = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
		self.btnCmdPause.SetToolTip( u"Pause text scrolling" )

		bSizer111.Add( self.btnCmdPause, 0, wx.ALL, 5 )

		self.btnCmdClear = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
		self.btnCmdClear.SetToolTip( u"Clear rendered text" )

		bSizer111.Add( self.btnCmdClear, 0, wx.ALL, 5 )

		self.btnCmdLineBreak = wx.BitmapButton( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, wx.BU_AUTODRAW|0 )
		self.btnCmdLineBreak.SetToolTip( u"Move to next line" )

		bSizer111.Add( self.btnCmdLineBreak, 0, wx.ALL, 5 )


		bSizer113.Add( bSizer111, 1, wx.EXPAND, 5 )


		bSizer110.Add( bSizer113, 0, wx.EXPAND, 5 )


		bSizer1091.Add( bSizer110, 0, wx.EXPAND, 5 )

		self.rich_ts = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.BORDER_DEFAULT|wx.HSCROLL|wx.VSCROLL|wx.WANTS_CHARS )
		bSizer1091.Add( self.rich_ts, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )

		self.panelSpacing = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,5 ), wx.TAB_TRAVERSAL )
		self.panelSpacing.Hide()

		bSizer1091.Add( self.panelSpacing, 0, 0, 0 )

		self.paneCommandParameters = wx.CollapsiblePane( self, wx.ID_ANY, u"Command Parameters...", wx.DefaultPosition, wx.DefaultSize, wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE )
		self.paneCommandParameters.Collapse( True )

		bSizer120 = wx.BoxSizer( wx.VERTICAL )

		self.panelSwitchAnimOptions = wx.Panel( self.paneCommandParameters.GetPane(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer116 = wx.BoxSizer( wx.HORIZONTAL )

		sbSizer39 = wx.StaticBoxSizer( wx.StaticBox( self.panelSwitchAnimOptions, wx.ID_ANY, u"Character Preview" ), wx.VERTICAL )

		self.bitmapPreviewAnim = wx.StaticBitmap( sbSizer39.GetStaticBox(), wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 256,192 ), 0 )
		sbSizer39.Add( self.bitmapPreviewAnim, 0, wx.ALL, 5 )


		bSizer116.Add( sbSizer39, 0, wx.RIGHT, 5 )

		sbSizer40 = wx.StaticBoxSizer( wx.StaticBox( self.panelSwitchAnimOptions, wx.ID_ANY, u"Parameters" ), wx.VERTICAL )

		bSizer133 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer133.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		fgSizer10 = wx.FlexGridSizer( 2, 2, 0, 0 )
		fgSizer10.SetFlexibleDirection( wx.BOTH )
		fgSizer10.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_staticText61 = wx.StaticText( sbSizer40.GetStaticBox(), wx.ID_ANY, u"Character", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText61.Wrap( -1 )

		fgSizer10.Add( self.m_staticText61, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )

		choiceChangeAnimCharNameChoices = []
		self.choiceChangeAnimCharName = wx.Choice( sbSizer40.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choiceChangeAnimCharNameChoices, 0 )
		self.choiceChangeAnimCharName.SetSelection( 0 )
		fgSizer10.Add( self.choiceChangeAnimCharName, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_staticText62 = wx.StaticText( sbSizer40.GetStaticBox(), wx.ID_ANY, u"Animation", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText62.Wrap( -1 )

		fgSizer10.Add( self.m_staticText62, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5 )

		choiceChangeAnimAnimNameChoices = []
		self.choiceChangeAnimAnimName = wx.Choice( sbSizer40.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choiceChangeAnimAnimNameChoices, 0 )
		self.choiceChangeAnimAnimName.SetSelection( 0 )
		fgSizer10.Add( self.choiceChangeAnimAnimName, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer133.Add( fgSizer10, 1, wx.EXPAND, 5 )


		bSizer133.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		sbSizer40.Add( bSizer133, 1, wx.EXPAND, 5 )

		self.checkSafeAnimOnly = wx.CheckBox( sbSizer40.GetStaticBox(), wx.ID_ANY, u"Restrict to safe animations", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkSafeAnimOnly.SetValue(True)
		self.checkSafeAnimOnly.SetToolTip( u"Some animations for specific purposes, e.g., moving the mouth during speech, are best left alone. Uncheck this box to allow using unsafe animations." )

		sbSizer40.Add( self.checkSafeAnimOnly, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

		self.m_staticText63 = wx.StaticText( sbSizer40.GetStaticBox(), wx.ID_ANY, u"Only characters linked to this event may be used. Edit linked characters from the Event editor.", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL )
		self.m_staticText63.Wrap( 180 )

		self.m_staticText63.Enable( False )

		sbSizer40.Add( self.m_staticText63, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer116.Add( sbSizer40, 1, wx.ALIGN_CENTER_VERTICAL, 5 )


		self.panelSwitchAnimOptions.SetSizer( bSizer116 )
		self.panelSwitchAnimOptions.Layout()
		bSizer116.Fit( self.panelSwitchAnimOptions )
		bSizer120.Add( self.panelSwitchAnimOptions, 1, wx.EXPAND |wx.ALL, 5 )

		self.panelSwitchDelayOptions = wx.Panel( self.paneCommandParameters.GetPane(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.panelSwitchDelayOptions.Hide()

		bSizer124 = wx.BoxSizer( wx.VERTICAL )

		bSizer125 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer125.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_staticText56 = wx.StaticText( self.panelSwitchDelayOptions, wx.ID_ANY, u"Delay", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText56.Wrap( -1 )

		bSizer125.Add( self.m_staticText56, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )

		choiceFramesChoices = []
		self.choiceFrames = wx.Choice( self.panelSwitchDelayOptions, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choiceFramesChoices, 0 )
		self.choiceFrames.SetSelection( 0 )
		bSizer125.Add( self.choiceFrames, 0, wx.ALL, 5 )


		bSizer125.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		bSizer124.Add( bSizer125, 1, wx.EXPAND, 5 )


		self.panelSwitchDelayOptions.SetSizer( bSizer124 )
		self.panelSwitchDelayOptions.Layout()
		bSizer124.Fit( self.panelSwitchDelayOptions )
		bSizer120.Add( self.panelSwitchDelayOptions, 0, wx.ALL|wx.EXPAND, 5 )


		self.paneCommandParameters.GetPane().SetSizer( bSizer120 )
		self.paneCommandParameters.GetPane().Layout()
		bSizer120.Fit( self.paneCommandParameters.GetPane() )
		bSizer1091.Add( self.paneCommandParameters, 0, wx.EXPAND |wx.ALL, 5 )

		self.staticlinePaneDivider = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		self.staticlinePaneDivider.Hide()

		bSizer1091.Add( self.staticlinePaneDivider, 0, wx.EXPAND|wx.RIGHT|wx.LEFT, 5 )

		self.paneStartingParameters = wx.CollapsiblePane( self, wx.ID_ANY, u"TalkScript Parameters...", wx.DefaultPosition, wx.DefaultSize, wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE )
		self.paneStartingParameters.Collapse( False )

		bSizer127 = wx.BoxSizer( wx.HORIZONTAL )

		sbSizer41 = wx.StaticBoxSizer( wx.StaticBox( self.paneStartingParameters.GetPane(), wx.ID_ANY, u"Character Preview - Start" ), wx.VERTICAL )

		self.bitmapCharPreview = wx.StaticBitmap( sbSizer41.GetStaticBox(), wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 256,192 ), 0 )
		sbSizer41.Add( self.bitmapCharPreview, 0, wx.ALL, 5 )


		bSizer127.Add( sbSizer41, 0, wx.ALIGN_CENTER_VERTICAL, 5 )

		sbSizer42 = wx.StaticBoxSizer( wx.StaticBox( self.paneStartingParameters.GetPane(), wx.ID_ANY, u"TalkScript Parameters" ), wx.VERTICAL )

		wSizer10 = wx.WrapSizer( wx.HORIZONTAL, 0 )

		bSizer129 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText60 = wx.StaticText( sbSizer42.GetStaticBox(), wx.ID_ANY, u"Target", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.m_staticText60.Wrap( -1 )

		self.m_staticText60.SetMinSize( wx.Size( 34,-1 ) )

		bSizer129.Add( self.m_staticText60, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

		choiceTargetCharacterChoices = [ u"(None)" ]
		self.choiceTargetCharacter = wx.Choice( sbSizer42.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choiceTargetCharacterChoices, 0 )
		self.choiceTargetCharacter.SetSelection( 0 )
		self.choiceTargetCharacter.SetToolTip( u"Character this TalkScript influences. If None is selected, the dialogue will still play but there will be no name attached to the box." )
		self.choiceTargetCharacter.SetMinSize( wx.Size( 80,-1 ) )

		bSizer129.Add( self.choiceTargetCharacter, 1, wx.ALL|wx.EXPAND, 5 )


		wSizer10.Add( bSizer129, 1, wx.EXPAND, 5 )

		bSizer130 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText59 = wx.StaticText( sbSizer42.GetStaticBox(), wx.ID_ANY, u"Pitch", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.m_staticText59.Wrap( -1 )

		self.m_staticText59.SetMinSize( wx.Size( 34,-1 ) )

		bSizer130.Add( self.m_staticText59, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_CENTER_HORIZONTAL, 5 )

		choiceMainPitchChoices = [ u"Low", u"Med", u"High", u"Low (no animation)", u"Med (no animation)", u"High (no animation)" ]
		self.choiceMainPitch = wx.Choice( sbSizer42.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choiceMainPitchChoices, 0 )
		self.choiceMainPitch.SetSelection( 0 )
		self.choiceMainPitch.SetToolTip( u"Pitch of sound made while printing characters. If no animation is selected, the animation won't be switched during talking, e.g., the mouth won't move during speech." )
		self.choiceMainPitch.SetMinSize( wx.Size( 80,-1 ) )

		bSizer130.Add( self.choiceMainPitch, 1, wx.ALL|wx.EXPAND, 5 )


		wSizer10.Add( bSizer130, 1, wx.EXPAND, 5 )


		sbSizer42.Add( wSizer10, 0, wx.EXPAND, 5 )

		sbSizer44 = wx.StaticBoxSizer( wx.StaticBox( sbSizer42.GetStaticBox(), wx.ID_ANY, u"Audio Voicelines" ), wx.VERTICAL )

		wSizer9 = wx.WrapSizer( wx.HORIZONTAL, 0 )

		self.btnSetVoiceline = wx.Button( sbSizer44.GetStaticBox(), wx.ID_ANY, u"Add voiceline...", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.btnSetVoiceline.Enable( False )

		wSizer9.Add( self.btnSetVoiceline, 1, wx.ALL|wx.EXPAND, 5 )

		self.btnDeleteVoiceline = wx.Button( sbSizer44.GetStaticBox(), wx.ID_ANY, u"Remove voiceline...", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.btnDeleteVoiceline.Enable( False )

		wSizer9.Add( self.btnDeleteVoiceline, 1, wx.ALL|wx.EXPAND, 5 )


		sbSizer44.Add( wSizer9, 1, wx.EXPAND, 5 )


		sbSizer42.Add( sbSizer44, 0, wx.ALL|wx.EXPAND, 5 )

		sbSizer43 = wx.StaticBoxSizer( wx.StaticBox( sbSizer42.GetStaticBox(), wx.ID_ANY, u"Animations at Triggers" ), wx.VERTICAL )

		bSizer126 = wx.BoxSizer( wx.HORIZONTAL )

		wSizer11 = wx.WrapSizer( wx.HORIZONTAL, 0 )

		bSizer131 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer131.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_staticText57 = wx.StaticText( sbSizer43.GetStaticBox(), wx.ID_ANY, u"On start", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.m_staticText57.Wrap( -1 )

		self.m_staticText57.SetMinSize( wx.Size( 50,-1 ) )

		bSizer131.Add( self.m_staticText57, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		choiceAnimOnStartChoices = [ u"(Continue Last)" ]
		self.choiceAnimOnStart = wx.Choice( sbSizer43.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choiceAnimOnStartChoices, 0 )
		self.choiceAnimOnStart.SetSelection( 0 )
		self.choiceAnimOnStart.SetMinSize( wx.Size( 100,-1 ) )

		bSizer131.Add( self.choiceAnimOnStart, 5, wx.ALL, 5 )


		bSizer131.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		wSizer11.Add( bSizer131, 1, wx.EXPAND, 5 )

		bSizer132 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer132.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_staticText58 = wx.StaticText( sbSizer43.GetStaticBox(), wx.ID_ANY, u"On done", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_RIGHT )
		self.m_staticText58.Wrap( -1 )

		self.m_staticText58.SetMinSize( wx.Size( 50,-1 ) )

		bSizer132.Add( self.m_staticText58, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		choiceAnimOnEndChoices = [ u"(Continue Last)" ]
		self.choiceAnimOnEnd = wx.Choice( sbSizer43.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choiceAnimOnEndChoices, 0 )
		self.choiceAnimOnEnd.SetSelection( 0 )
		self.choiceAnimOnEnd.SetMinSize( wx.Size( 100,-1 ) )

		bSizer132.Add( self.choiceAnimOnEnd, 5, wx.ALL, 5 )


		bSizer132.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		wSizer11.Add( bSizer132, 1, wx.EXPAND, 5 )


		bSizer126.Add( wSizer11, 1, wx.EXPAND, 5 )

		self.btnTogglePreview = wx.Button( sbSizer43.GetStaticBox(), wx.ID_ANY, u"Toggle\npreview", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer126.Add( self.btnTogglePreview, 0, wx.ALL|wx.EXPAND, 5 )


		sbSizer43.Add( bSizer126, 1, wx.EXPAND, 5 )

		self.m_staticText64 = wx.StaticText( sbSizer43.GetStaticBox(), wx.ID_ANY, u"No preview is available when continuing the last animation\nas the character state is not known.", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL )
		self.m_staticText64.Wrap( -1 )

		self.m_staticText64.Enable( False )

		sbSizer43.Add( self.m_staticText64, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )


		sbSizer42.Add( sbSizer43, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer127.Add( sbSizer42, 1, wx.ALIGN_CENTER_VERTICAL|wx.LEFT, 5 )


		self.paneStartingParameters.GetPane().SetSizer( bSizer127 )
		self.paneStartingParameters.GetPane().Layout()
		bSizer127.Fit( self.paneStartingParameters.GetPane() )
		bSizer1091.Add( self.paneStartingParameters, 0, wx.EXPAND |wx.ALL, 5 )


		bSizer106.Add( bSizer1091, 1, wx.EXPAND, 5 )

		self.m_staticline30 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
		bSizer106.Add( self.m_staticline30, 0, wx.EXPAND|wx.TOP|wx.BOTTOM|wx.RIGHT, 5 )

		bSizer108 = wx.BoxSizer( wx.VERTICAL )


		bSizer108.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		sbSizer36 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Line Wrapping" ), wx.VERTICAL )

		self.checkAutoLineWrap = wx.CheckBox( sbSizer36.GetStaticBox(), wx.ID_ANY, u"Apply line wrapping when converting", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkAutoLineWrap.SetValue(True)
		self.checkAutoLineWrap.SetToolTip( u"Applies automatic line wrapping to the result to ensure no lines go off-screen where possible." )

		sbSizer36.Add( self.checkAutoLineWrap, 0, wx.ALL, 5 )

		self.checkRestrictOperation = wx.CheckBox( sbSizer36.GetStaticBox(), wx.ID_ANY, u"Restrict to current section", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkRestrictOperation.SetToolTip( u"Restrict the below operations to only the previewed section. If unchecked, operations will apply to the entire text." )

		sbSizer36.Add( self.checkRestrictOperation, 0, wx.ALL, 5 )

		bSizer1081 = wx.BoxSizer( wx.VERTICAL )

		self.btnWrapToBreaks = wx.Button( sbSizer36.GetStaticBox(), wx.ID_ANY, u"Add automatic custom line breaks", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.btnWrapToBreaks.SetToolTip( u"Applies a pass of the line wrapper and integrates the result into the text itself as line break commands. Useful if the line wrapper is too aggressive or there are custom breaks in the text." )

		bSizer1081.Add( self.btnWrapToBreaks, 0, wx.EXPAND|wx.TOP|wx.RIGHT|wx.LEFT, 5 )

		self.btnCullLineBreaks = wx.Button( sbSizer36.GetStaticBox(), wx.ID_ANY, u"Remove custom line breaks", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.btnCullLineBreaks.SetToolTip( u"Removes line break commands." )

		bSizer1081.Add( self.btnCullLineBreaks, 0, wx.ALL|wx.EXPAND, 5 )


		sbSizer36.Add( bSizer1081, 1, wx.EXPAND, 5 )


		bSizer108.Add( sbSizer36, 0, wx.EXPAND, 5 )


		bSizer108.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		sbSizer35 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Text Rendering Preview" ), wx.VERTICAL )

		self.bitmapPreview = wx.StaticBitmap( sbSizer35.GetStaticBox(), wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 256,192 ), 0 )
		sbSizer35.Add( self.bitmapPreview, 0, wx.ALL, 5 )


		bSizer108.Add( sbSizer35, 0, wx.ALIGN_CENTER_HORIZONTAL, 5 )

		bSizer109 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer109.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.btnConfirm = wx.Button( self, wx.ID_ANY, u"Confirm", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer109.Add( self.btnConfirm, 0, wx.ALL, 5 )

		self.btnCancel = wx.Button( self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer109.Add( self.btnCancel, 0, wx.ALL, 5 )


		bSizer108.Add( bSizer109, 0, wx.EXPAND, 5 )


		bSizer108.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		bSizer106.Add( bSizer108, 0, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( bSizer106 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.btnColorBlack.Bind( wx.EVT_BUTTON, self.btnColorBlackOnButtonClick )
		self.btnColorWhite.Bind( wx.EVT_BUTTON, self.btnColorWhiteOnButtonClick )
		self.btnColorRed.Bind( wx.EVT_BUTTON, self.btnColorRedOnButtonClick )
		self.btnColorGreen.Bind( wx.EVT_BUTTON, self.btnColorGreenOnButtonClick )
		self.btnCmdAnim.Bind( wx.EVT_BUTTON, self.btnCmdAnimOnButtonClick )
		self.btnCmdDelay.Bind( wx.EVT_BUTTON, self.btnCmdDelayOnButtonClick )
		self.btnCmdPause.Bind( wx.EVT_BUTTON, self.btnCmdPauseOnButtonClick )
		self.btnCmdClear.Bind( wx.EVT_BUTTON, self.btnCmdClearOnButtonClick )
		self.btnCmdLineBreak.Bind( wx.EVT_BUTTON, self.btnCmdLineBreakOnButtonClick )
		self.rich_ts.Bind( wx.EVT_LEFT_DOWN, self.rich_tsOnLeftDown )
		self.rich_ts.Bind( wx.richtext.EVT_RICHTEXT_CHARACTER, self.rich_tsOnRichTextCharacter )
		self.rich_ts.Bind( wx.richtext.EVT_RICHTEXT_DELETE, self.rich_tsOnRichTextDelete )
		self.rich_ts.Bind( wx.EVT_TEXT, self.rich_tsOnText )
		self.paneCommandParameters.Bind( wx.EVT_COLLAPSIBLEPANE_CHANGED, self.paneCommandParametersOnCollapsiblePaneChanged )
		self.choiceChangeAnimCharName.Bind( wx.EVT_CHOICE, self.choiceChangeAnimCharNameOnChoice )
		self.choiceChangeAnimAnimName.Bind( wx.EVT_CHOICE, self.choiceChangeAnimAnimNameOnChoice )
		self.checkSafeAnimOnly.Bind( wx.EVT_CHECKBOX, self.checkSafeAnimOnlyOnCheckBox )
		self.paneStartingParameters.Bind( wx.EVT_COLLAPSIBLEPANE_CHANGED, self.paneStartingParametersOnCollapsiblePaneChanged )
		self.choiceTargetCharacter.Bind( wx.EVT_CHOICE, self.choiceTargetCharacterOnChoice )
		self.choiceMainPitch.Bind( wx.EVT_CHOICE, self.choiceMainPitchOnChoice )
		self.choiceAnimOnStart.Bind( wx.EVT_CHOICE, self.choiceAnimOnStartOnChoice )
		self.choiceAnimOnEnd.Bind( wx.EVT_CHOICE, self.choiceAnimOnEndOnChoice )
		self.btnTogglePreview.Bind( wx.EVT_BUTTON, self.btnTogglePreviewOnButtonClick )
		self.btnWrapToBreaks.Bind( wx.EVT_BUTTON, self.btnWrapToBreaksOnButtonClick )
		self.btnCullLineBreaks.Bind( wx.EVT_BUTTON, self.btnCullLineBreaksOnButtonClick )
		self.btnConfirm.Bind( wx.EVT_BUTTON, self.btnConfirmOnButtonClick )
		self.btnCancel.Bind( wx.EVT_BUTTON, self.btnCancelOnButtonClick )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def btnColorBlackOnButtonClick( self, event ):
		event.Skip()

	def btnColorWhiteOnButtonClick( self, event ):
		event.Skip()

	def btnColorRedOnButtonClick( self, event ):
		event.Skip()

	def btnColorGreenOnButtonClick( self, event ):
		event.Skip()

	def btnCmdAnimOnButtonClick( self, event ):
		event.Skip()

	def btnCmdDelayOnButtonClick( self, event ):
		event.Skip()

	def btnCmdPauseOnButtonClick( self, event ):
		event.Skip()

	def btnCmdClearOnButtonClick( self, event ):
		event.Skip()

	def btnCmdLineBreakOnButtonClick( self, event ):
		event.Skip()

	def rich_tsOnLeftDown( self, event ):
		event.Skip()

	def rich_tsOnRichTextCharacter( self, event ):
		event.Skip()

	def rich_tsOnRichTextDelete( self, event ):
		event.Skip()

	def rich_tsOnText( self, event ):
		event.Skip()

	def paneCommandParametersOnCollapsiblePaneChanged( self, event ):
		event.Skip()

	def choiceChangeAnimCharNameOnChoice( self, event ):
		event.Skip()

	def choiceChangeAnimAnimNameOnChoice( self, event ):
		event.Skip()

	def checkSafeAnimOnlyOnCheckBox( self, event ):
		event.Skip()

	def paneStartingParametersOnCollapsiblePaneChanged( self, event ):
		event.Skip()

	def choiceTargetCharacterOnChoice( self, event ):
		event.Skip()

	def choiceMainPitchOnChoice( self, event ):
		event.Skip()

	def choiceAnimOnStartOnChoice( self, event ):
		event.Skip()

	def choiceAnimOnEndOnChoice( self, event ):
		event.Skip()

	def btnTogglePreviewOnButtonClick( self, event ):
		event.Skip()

	def btnWrapToBreaksOnButtonClick( self, event ):
		event.Skip()

	def btnCullLineBreaksOnButtonClick( self, event ):
		event.Skip()

	def btnConfirmOnButtonClick( self, event ):
		event.Skip()

	def btnCancelOnButtonClick( self, event ):
		event.Skip()


###########################################################################
## Class panelAnimPlayback
###########################################################################

class panelAnimPlayback ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 256,192 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		bSizer128 = wx.BoxSizer( wx.VERTICAL )

		self.bitmapAnim = wx.StaticBitmap( self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 256,192 ), 0 )
		bSizer128.Add( self.bitmapAnim, 0, 0, 0 )


		self.SetSizer( bSizer128 )
		self.Layout()

	def __del__( self ):
		pass


###########################################################################
## Class Editor
###########################################################################

class Editor ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"widebrim editor", pos = wx.DefaultPosition, size = wx.Size( 960,768 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.Size( 960,768 ), wx.DefaultSize )
		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_ACTIVEBORDER ) )

		self.menubar = wx.MenuBar( 0 )
		self.menuFile = wx.Menu()
		self.submenuFileCompile = wx.MenuItem( self.menuFile, wx.ID_ANY, u"Compile patch...", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuFile.Append( self.submenuFileCompile )

		self.menuFile.AppendSeparator()

		self.submenuFileAbout = wx.MenuItem( self.menuFile, wx.ID_ANY, u"About", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuFile.Append( self.submenuFileAbout )

		self.submenuFileReturnToStartup = wx.MenuItem( self.menuFile, wx.ID_ANY, u"Return to startup...", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuFile.Append( self.submenuFileReturnToStartup )

		self.menubar.Append( self.menuFile, u"File" )

		self.menuEditor = wx.Menu()
		self.m_menuItem9 = wx.MenuItem( self.menuEditor, wx.ID_ANY, u"Name to Character ID map", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuEditor.Append( self.m_menuItem9 )

		self.menuEditor.AppendSeparator()

		self.m_menuItem14 = wx.MenuItem( self.menuEditor, wx.ID_ANY, u"Generate unused databases", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuEditor.Append( self.m_menuItem14 )

		self.m_menuItem16 = wx.MenuItem( self.menuEditor, wx.ID_ANY, u"Override built databases...", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuEditor.Append( self.m_menuItem16 )

		self.menuEditor.AppendSeparator()

		self.submenuEditorOptimiseFs = wx.MenuItem( self.menuEditor, wx.ID_ANY, u"Optimise filesystem...", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuEditor.Append( self.submenuEditorOptimiseFs )

		self.menuEditor.AppendSeparator()

		self.menuVirtualAbstraction = wx.Menu()
		self.menuAbstractionLow = wx.MenuItem( self.menuVirtualAbstraction, wx.ID_ANY, u"Low abstraction level (powerful; no protections applied)", wx.EmptyString, wx.ITEM_RADIO )
		self.menuVirtualAbstraction.Append( self.menuAbstractionLow )
		self.menuAbstractionLow.Check( True )

		self.menuAbstractionMed = wx.MenuItem( self.menuVirtualAbstraction, wx.ID_ANY, u"Medium abstraction level (balanced; specialized entry)", wx.EmptyString, wx.ITEM_RADIO )
		self.menuVirtualAbstraction.Append( self.menuAbstractionMed )

		self.menuAbstractionHigh = wx.MenuItem( self.menuVirtualAbstraction, wx.ID_ANY, u"High abstraction level (safest; virtual scripting)", wx.EmptyString, wx.ITEM_RADIO )
		self.menuVirtualAbstraction.Append( self.menuAbstractionHigh )

		self.menuVirtualAbstraction.AppendSeparator()

		self.menuVirtualScriptLossy = wx.MenuItem( self.menuVirtualAbstraction, wx.ID_ANY, u"Permit lossy operations", wx.EmptyString, wx.ITEM_CHECK )
		self.menuVirtualAbstraction.Append( self.menuVirtualScriptLossy )
		self.menuVirtualScriptLossy.Enable( False )
		self.menuVirtualScriptLossy.Check( True )

		self.menuVirtualAbstraction.AppendSeparator()

		self.submenuDefinition = wx.Menu()
		self.menuDefinitionLoad = wx.MenuItem( self.submenuDefinition, wx.ID_ANY, u"Load scripting helper definitions...", wx.EmptyString, wx.ITEM_NORMAL )
		self.submenuDefinition.Append( self.menuDefinitionLoad )

		self.menuDefinitionSave = wx.MenuItem( self.submenuDefinition, wx.ID_ANY, u"Save scripting helper definitions...", wx.EmptyString, wx.ITEM_NORMAL )
		self.submenuDefinition.Append( self.menuDefinitionSave )

		self.menuDefinitionGenerate = wx.MenuItem( self.submenuDefinition, wx.ID_ANY, u"Generate scripting helper definitions (experimental)", wx.EmptyString, wx.ITEM_NORMAL )
		self.submenuDefinition.Append( self.menuDefinitionGenerate )

		self.menuVirtualAbstraction.AppendSubMenu( self.submenuDefinition, u"Modify instruction helper definitions..." )

		self.menuEditor.AppendSubMenu( self.menuVirtualAbstraction, u"Script editing preferences..." )

		self.menuOverviewPreferences = wx.Menu()
		self.menuPrefOverviewEnableEvtInf = wx.MenuItem( self.menuOverviewPreferences, wx.ID_ANY, u"Show event comments", wx.EmptyString, wx.ITEM_CHECK )
		self.menuOverviewPreferences.Append( self.menuPrefOverviewEnableEvtInf )

		self.menuEditor.AppendSubMenu( self.menuOverviewPreferences, u"Overview preferences..." )

		self.menubar.Append( self.menuEditor, u"Editor" )

		self.menuPreview = wx.Menu()
		self.m_menuItem5 = wx.MenuItem( self.menuPreview, wx.ID_ANY, u"Start on select", wx.EmptyString, wx.ITEM_CHECK )
		self.menuPreview.Append( self.m_menuItem5 )
		self.m_menuItem5.Check( True )

		self.submenuEnginePause = wx.MenuItem( self.menuPreview, wx.ID_ANY, u"Pause", wx.EmptyString, wx.ITEM_CHECK )
		self.menuPreview.Append( self.submenuEnginePause )

		self.submenuEngineFramerate = wx.Menu()
		self.framesHalf = wx.MenuItem( self.submenuEngineFramerate, wx.ID_ANY, u"~30fps", wx.EmptyString, wx.ITEM_RADIO )
		self.submenuEngineFramerate.Append( self.framesHalf )

		self.framesFull = wx.MenuItem( self.submenuEngineFramerate, wx.ID_ANY, u"~60fps (fast, choppy)", wx.EmptyString, wx.ITEM_RADIO )
		self.submenuEngineFramerate.Append( self.framesFull )

		self.framesExtended = wx.MenuItem( self.submenuEngineFramerate, wx.ID_ANY, u"Window Limit (smoother)", wx.EmptyString, wx.ITEM_RADIO )
		self.submenuEngineFramerate.Append( self.framesExtended )
		self.framesExtended.Check( True )

		self.menuPreview.AppendSubMenu( self.submenuEngineFramerate, u"Modify framerate..." )

		self.submenuEngineSpeed = wx.Menu()
		self.speedRealtime = wx.MenuItem( self.submenuEngineSpeed, wx.ID_ANY, u"1.00x (Realtime)", wx.EmptyString, wx.ITEM_RADIO )
		self.submenuEngineSpeed.Append( self.speedRealtime )

		self.speedDouble = wx.MenuItem( self.submenuEngineSpeed, wx.ID_ANY, u"2.00x", wx.EmptyString, wx.ITEM_RADIO )
		self.submenuEngineSpeed.Append( self.speedDouble )

		self.speedQuadruple = wx.MenuItem( self.submenuEngineSpeed, wx.ID_ANY, u"4.00x", wx.EmptyString, wx.ITEM_RADIO )
		self.submenuEngineSpeed.Append( self.speedQuadruple )

		self.menuPreview.AppendSubMenu( self.submenuEngineSpeed, u"Modify speed..." )

		self.m_menuItem1 = wx.MenuItem( self.menuPreview, wx.ID_ANY, u"Edit state flags", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuPreview.Append( self.m_menuItem1 )

		self.menuPreview.AppendSeparator()

		self.m_menuItem3 = wx.MenuItem( self.menuPreview, wx.ID_ANY, u"Load from save...", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuPreview.Append( self.m_menuItem3 )

		self.menubar.Append( self.menuPreview, u"Preview" )

		self.menuCleanup = wx.Menu()
		self.submenuCleanupAssets = wx.MenuItem( self.menuCleanup, wx.ID_ANY, u"Remove unused assets...", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuCleanup.Append( self.submenuCleanupAssets )

		self.submenuCleanupEventFlags = wx.MenuItem( self.menuCleanup, wx.ID_ANY, u"Remove unused flags....", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuCleanup.Append( self.submenuCleanupEventFlags )

		self.submenuCleanupText = wx.MenuItem( self.menuCleanup, wx.ID_ANY, u"Remove unused text...", wx.EmptyString, wx.ITEM_NORMAL )
		self.menuCleanup.Append( self.submenuCleanupText )

		self.menubar.Append( self.menuCleanup, u"Cleanup" )

		self.SetMenuBar( self.menubar )

		bSizer10 = wx.BoxSizer( wx.HORIZONTAL )

		self.auiTabs = wx.aui.AuiNotebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_NB_DEFAULT_STYLE )

		bSizer10.Add( self.auiTabs, 1, wx.EXPAND, 5 )

		self.m_staticline5 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
		bSizer10.Add( self.m_staticline5, 0, wx.EXPAND, 5 )

		bSizer11 = wx.BoxSizer( wx.VERTICAL )

		widebrimPreviewSizer = wx.BoxSizer( wx.VERTICAL )

		self.panelWidebrimQuickControls = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.panelWidebrimQuickControls.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
		self.panelWidebrimQuickControls.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_MENU ) )

		bSizer50 = wx.BoxSizer( wx.VERTICAL )

		self.m_panel7 = wx.Panel( self.panelWidebrimQuickControls, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizer14 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText7 = wx.StaticText( self.m_panel7, wx.ID_ANY, u"Preview", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText7.Wrap( -1 )

		bSizer14.Add( self.m_staticText7, 0, wx.ALIGN_CENTER|wx.BOTTOM|wx.LEFT|wx.RIGHT|wx.TOP, 5 )


		bSizer14.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.widebrimButtonPausePlay = wx.Button( self.m_panel7, wx.ID_ANY, u"⏸", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		bSizer14.Add( self.widebrimButtonPausePlay, 0, 0, 5 )

		self.widebrimButtonRestartState = wx.Button( self.m_panel7, wx.ID_ANY, u"🔁", wx.DefaultPosition, wx.DefaultSize, wx.BU_EXACTFIT )
		self.widebrimButtonRestartState.SetToolTip( u"Restart the widebrim engine. May require tabbing back into editors to reconnect state." )

		bSizer14.Add( self.widebrimButtonRestartState, 0, wx.LEFT|wx.RIGHT, 3 )


		self.m_panel7.SetSizer( bSizer14 )
		self.m_panel7.Layout()
		bSizer14.Fit( self.m_panel7 )
		bSizer50.Add( self.m_panel7, 1, wx.ALL|wx.EXPAND, 2 )


		self.panelWidebrimQuickControls.SetSizer( bSizer50 )
		self.panelWidebrimQuickControls.Layout()
		bSizer50.Fit( self.panelWidebrimQuickControls )
		widebrimPreviewSizer.Add( self.panelWidebrimQuickControls, 0, wx.EXPAND, 0 )

		self.m_staticline2 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		widebrimPreviewSizer.Add( self.m_staticline2, 0, wx.EXPAND, 5 )

		self.panelWidebrimInjection = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.CLIP_CHILDREN|wx.TAB_TRAVERSAL|wx.TRANSPARENT_WINDOW )
		self.panelWidebrimInjection.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ) )
		self.panelWidebrimInjection.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_APPWORKSPACE ) )
		self.panelWidebrimInjection.SetMinSize( wx.Size( 256,384 ) )
		self.panelWidebrimInjection.SetMaxSize( wx.Size( 256,384 ) )

		widebrimPreviewSizer.Add( self.panelWidebrimInjection, 1, wx.ALIGN_CENTER, 5 )

		self.m_staticline4 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		widebrimPreviewSizer.Add( self.m_staticline4, 0, wx.EXPAND, 5 )

		self.panelRomParameters = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.panelRomParameters.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_MENU ) )

		bSizer34 = wx.BoxSizer( wx.VERTICAL )

		bSizer19 = wx.BoxSizer( wx.HORIZONTAL )

		self.previewIcon = wx.StaticBitmap( self.panelRomParameters, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.previewIcon.SetToolTip( u"Icon shown on the System Menu before starting the game." )
		self.previewIcon.SetMinSize( wx.Size( 32,32 ) )

		bSizer19.Add( self.previewIcon, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		self.m_staticline3 = wx.StaticLine( self.panelRomParameters, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
		bSizer19.Add( self.m_staticline3, 0, wx.BOTTOM|wx.EXPAND|wx.RIGHT|wx.TOP, 5 )

		fgSizer1 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer1.SetFlexibleDirection( wx.BOTH )
		fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_staticText13 = wx.StaticText( self.panelRomParameters, wx.ID_ANY, u"Title", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText13.Wrap( -1 )

		fgSizer1.Add( self.m_staticText13, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

		self.romTextName = wx.TextCtrl( self.panelRomParameters, wx.ID_ANY, u"Professor Layton and the Diabolical Box", wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_WORDWRAP )
		self.romTextName.SetMaxLength( 256 )
		self.romTextName.SetMinSize( wx.Size( 150,-1 ) )

		fgSizer1.Add( self.romTextName, 0, wx.BOTTOM|wx.LEFT|wx.TOP, 5 )

		self.m_staticText14 = wx.StaticText( self.panelRomParameters, wx.ID_ANY, u"Code", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText14.Wrap( -1 )

		fgSizer1.Add( self.m_staticText14, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )

		self.romTextCode = wx.TextCtrl( self.panelRomParameters, wx.ID_ANY, u"FFFF", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.romTextCode.SetMaxLength( 4 )
		self.romTextCode.SetToolTip( u"Used for identification purposes. Changing this value may interfere with mods using this to recognise this ROM as Professor Layton." )

		fgSizer1.Add( self.romTextCode, 0, wx.ALL, 5 )


		bSizer19.Add( fgSizer1, 1, wx.EXPAND, 5 )


		bSizer34.Add( bSizer19, 1, wx.ALIGN_CENTER, 5 )

		self.forceSync = wx.Button( self.panelRomParameters, wx.ID_ANY, u"Sync Changes", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer34.Add( self.forceSync, 0, wx.ALL|wx.EXPAND, 5 )


		self.panelRomParameters.SetSizer( bSizer34 )
		self.panelRomParameters.Layout()
		bSizer34.Fit( self.panelRomParameters )
		widebrimPreviewSizer.Add( self.panelRomParameters, 0, wx.EXPAND, 5 )

		self.panelWidebrimInjection1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.TAB_TRAVERSAL )
		self.panelWidebrimInjection1.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_MENU ) )
		self.panelWidebrimInjection1.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_MENU ) )

		widebrimPreviewSizer.Add( self.panelWidebrimInjection1, 1, wx.EXPAND, 5 )


		bSizer11.Add( widebrimPreviewSizer, 1, wx.EXPAND, 5 )


		bSizer10.Add( bSizer11, 0, wx.EXPAND, 5 )


		self.SetSizer( bSizer10 )
		self.Layout()

		self.Centre( wx.BOTH )

		# Connect Events
		self.Bind( wx.EVT_MENU, self.submenuFileCompileOnMenuSelection, id = self.submenuFileCompile.GetId() )
		self.Bind( wx.EVT_MENU, self.submenuFileReturnToStartupOnMenuSelection, id = self.submenuFileReturnToStartup.GetId() )
		self.Bind( wx.EVT_MENU, self.submenuEditorOptimiseFsOnMenuSelection, id = self.submenuEditorOptimiseFs.GetId() )
		self.Bind( wx.EVT_MENU, self.menuAbstractionLowOnMenuSelection, id = self.menuAbstractionLow.GetId() )
		self.Bind( wx.EVT_MENU, self.menuAbstractionMedOnMenuSelection, id = self.menuAbstractionMed.GetId() )
		self.Bind( wx.EVT_MENU, self.menuAbstractionHighOnMenuSelection, id = self.menuAbstractionHigh.GetId() )
		self.Bind( wx.EVT_MENU, self.menuVirtualScriptLossyOnMenuSelection, id = self.menuVirtualScriptLossy.GetId() )
		self.Bind( wx.EVT_MENU, self.menuDefinitionLoadOnMenuSelection, id = self.menuDefinitionLoad.GetId() )
		self.Bind( wx.EVT_MENU, self.menuDefinitionSaveOnMenuSelection, id = self.menuDefinitionSave.GetId() )
		self.Bind( wx.EVT_MENU, self.menuDefinitionGenerateOnMenuSelection, id = self.menuDefinitionGenerate.GetId() )
		self.Bind( wx.EVT_MENU, self.menuPrefOverviewEnableEvtInfOnMenuSelection, id = self.menuPrefOverviewEnableEvtInf.GetId() )
		self.Bind( wx.EVT_MENU, self.submenuEnginePauseOnMenuSelection, id = self.submenuEnginePause.GetId() )
		self.Bind( wx.EVT_MENU, self.framesHalfOnMenuSelection, id = self.framesHalf.GetId() )
		self.Bind( wx.EVT_MENU, self.framesFullOnMenuSelection, id = self.framesFull.GetId() )
		self.Bind( wx.EVT_MENU, self.framesExtendedOnMenuSelection, id = self.framesExtended.GetId() )
		self.Bind( wx.EVT_MENU, self.speedRealtimeOnMenuSelection, id = self.speedRealtime.GetId() )
		self.Bind( wx.EVT_MENU, self.speedDoubleOnMenuSelection, id = self.speedDouble.GetId() )
		self.Bind( wx.EVT_MENU, self.speedQuadrupleOnMenuSelection, id = self.speedQuadruple.GetId() )
		self.Bind( wx.EVT_MENU, self.submenuCleanupAssetsOnMenuSelection, id = self.submenuCleanupAssets.GetId() )
		self.Bind( wx.EVT_MENU, self.submenuCleanupEventFlagsOnMenuSelection, id = self.submenuCleanupEventFlags.GetId() )
		self.Bind( wx.EVT_MENU, self.submenuCleanupTextOnMenuSelection, id = self.submenuCleanupText.GetId() )
		self.auiTabs.Bind( wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.auiTabsOnAuiNotebookPageChanged )
		self.auiTabs.Bind( wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.auiTabsOnAuiNotebookPageClose )
		self.widebrimButtonPausePlay.Bind( wx.EVT_BUTTON, self.widebrimButtonPausePlayOnButtonClick )
		self.widebrimButtonRestartState.Bind( wx.EVT_BUTTON, self.widebrimButtonRestartStateOnButtonClick )
		self.panelWidebrimInjection.Bind( wx.EVT_LEFT_DOWN, self.panelWidebrimInjectionOnLeftDown )
		self.panelWidebrimInjection.Bind( wx.EVT_LEFT_UP, self.panelWidebrimInjectionOnLeftUp )
		self.panelWidebrimInjection.Bind( wx.EVT_MOTION, self.panelWidebrimInjectionOnMotion )
		self.forceSync.Bind( wx.EVT_BUTTON, self.forceSyncOnButtonClick )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def submenuFileCompileOnMenuSelection( self, event ):
		event.Skip()

	def submenuFileReturnToStartupOnMenuSelection( self, event ):
		event.Skip()

	def submenuEditorOptimiseFsOnMenuSelection( self, event ):
		event.Skip()

	def menuAbstractionLowOnMenuSelection( self, event ):
		event.Skip()

	def menuAbstractionMedOnMenuSelection( self, event ):
		event.Skip()

	def menuAbstractionHighOnMenuSelection( self, event ):
		event.Skip()

	def menuVirtualScriptLossyOnMenuSelection( self, event ):
		event.Skip()

	def menuDefinitionLoadOnMenuSelection( self, event ):
		event.Skip()

	def menuDefinitionSaveOnMenuSelection( self, event ):
		event.Skip()

	def menuDefinitionGenerateOnMenuSelection( self, event ):
		event.Skip()

	def menuPrefOverviewEnableEvtInfOnMenuSelection( self, event ):
		event.Skip()

	def submenuEnginePauseOnMenuSelection( self, event ):
		event.Skip()

	def framesHalfOnMenuSelection( self, event ):
		event.Skip()

	def framesFullOnMenuSelection( self, event ):
		event.Skip()

	def framesExtendedOnMenuSelection( self, event ):
		event.Skip()

	def speedRealtimeOnMenuSelection( self, event ):
		event.Skip()

	def speedDoubleOnMenuSelection( self, event ):
		event.Skip()

	def speedQuadrupleOnMenuSelection( self, event ):
		event.Skip()

	def submenuCleanupAssetsOnMenuSelection( self, event ):
		event.Skip()

	def submenuCleanupEventFlagsOnMenuSelection( self, event ):
		event.Skip()

	def submenuCleanupTextOnMenuSelection( self, event ):
		event.Skip()

	def auiTabsOnAuiNotebookPageChanged( self, event ):
		event.Skip()

	def auiTabsOnAuiNotebookPageClose( self, event ):
		event.Skip()

	def widebrimButtonPausePlayOnButtonClick( self, event ):
		event.Skip()

	def widebrimButtonRestartStateOnButtonClick( self, event ):
		event.Skip()

	def panelWidebrimInjectionOnLeftDown( self, event ):
		event.Skip()

	def panelWidebrimInjectionOnLeftUp( self, event ):
		event.Skip()

	def panelWidebrimInjectionOnMotion( self, event ):
		event.Skip()

	def forceSyncOnButtonClick( self, event ):
		event.Skip()


###########################################################################
## Class pageOverview
###########################################################################

class pageOverview ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 640,640 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_MENU ) )
		self.SetMinSize( wx.Size( 480,480 ) )

		bSizer18 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer19 = wx.BoxSizer( wx.VERTICAL )

		self.btnCreateNew = wx.Button( self, wx.ID_ANY, u"Create new...", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer19.Add( self.btnCreateNew, 0, wx.ALL|wx.EXPAND, 5 )

		self.btnDuplicate = wx.Button( self, wx.ID_ANY, u"Duplicate...", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer19.Add( self.btnDuplicate, 0, wx.ALL|wx.EXPAND, 5 )

		self.btnDelete = wx.Button( self, wx.ID_ANY, u"Delete", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer19.Add( self.btnDelete, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_staticline81 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer19.Add( self.m_staticline81, 0, wx.EXPAND |wx.ALL, 5 )

		self.btnGetRef = wx.Button( self, wx.ID_ANY, u"Get References", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer19.Add( self.btnGetRef, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_staticline8 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer19.Add( self.m_staticline8, 0, wx.ALL|wx.EXPAND, 5 )

		self.btnChangeId = wx.Button( self, wx.ID_ANY, u"Change ID...", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer19.Add( self.btnChangeId, 0, wx.ALL|wx.EXPAND, 5 )

		self.btnChangeName = wx.Button( self, wx.ID_ANY, u"Rename", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer19.Add( self.btnChangeName, 0, wx.ALL|wx.EXPAND, 5 )

		self.btnRemovable = wx.Button( self, wx.ID_ANY, u"Set removable", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer19.Add( self.btnRemovable, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_staticline25 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer19.Add( self.m_staticline25, 0, wx.EXPAND |wx.ALL, 5 )

		self.btnNewCondition = wx.Button( self, wx.ID_ANY, u"New condition...", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer19.Add( self.btnNewCondition, 0, wx.ALL|wx.EXPAND, 5 )

		self.btnEditCondition = wx.Button( self, wx.ID_ANY, u"Edit condition...", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer19.Add( self.btnEditCondition, 0, wx.ALL|wx.EXPAND, 5 )

		self.btnDeleteCondition = wx.Button( self, wx.ID_ANY, u"Delete condition", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer19.Add( self.btnDeleteCondition, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer18.Add( bSizer19, 1, wx.EXPAND, 5 )

		self.treeOverview = wx.TreeCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT )
		bSizer18.Add( self.treeOverview, 5, wx.ALL|wx.EXPAND, 5 )


		self.SetSizer( bSizer18 )
		self.Layout()

		# Connect Events
		self.btnCreateNew.Bind( wx.EVT_BUTTON, self.btnCreateNewOnButtonClick )
		self.btnDuplicate.Bind( wx.EVT_BUTTON, self.btnDuplicateOnButtonClick )
		self.btnDelete.Bind( wx.EVT_BUTTON, self.btnDeleteOnButtonClick )
		self.btnGetRef.Bind( wx.EVT_BUTTON, self.btnGetRefOnButtonClick )
		self.btnChangeId.Bind( wx.EVT_BUTTON, self.btnChangeIdOnButtonClick )
		self.btnChangeName.Bind( wx.EVT_BUTTON, self.btnChangeNameOnButtonClick )
		self.btnRemovable.Bind( wx.EVT_BUTTON, self.btnRemovableOnButtonClick )
		self.btnNewCondition.Bind( wx.EVT_BUTTON, self.btnNewConditionOnButtonClick )
		self.btnEditCondition.Bind( wx.EVT_BUTTON, self.btnEditConditionOnButtonClick )
		self.treeOverview.Bind( wx.EVT_TREE_ITEM_ACTIVATED, self.treeOverviewOnTreeItemActivated )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def btnCreateNewOnButtonClick( self, event ):
		event.Skip()

	def btnDuplicateOnButtonClick( self, event ):
		event.Skip()

	def btnDeleteOnButtonClick( self, event ):
		event.Skip()

	def btnGetRefOnButtonClick( self, event ):
		event.Skip()

	def btnChangeIdOnButtonClick( self, event ):
		event.Skip()

	def btnChangeNameOnButtonClick( self, event ):
		event.Skip()

	def btnRemovableOnButtonClick( self, event ):
		event.Skip()

	def btnNewConditionOnButtonClick( self, event ):
		event.Skip()

	def btnEditConditionOnButtonClick( self, event ):
		event.Skip()

	def treeOverviewOnTreeItemActivated( self, event ):
		event.Skip()


###########################################################################
## Class pageFullRomControl
###########################################################################

class pageFullRomControl ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 640,640 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		self.SetMinSize( wx.Size( 480,480 ) )

		bSizer18 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_treeCtrl1 = wx.TreeCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_DEFAULT_STYLE )
		bSizer18.Add( self.m_treeCtrl1, 5, wx.ALL|wx.EXPAND, 5 )

		bSizer19 = wx.BoxSizer( wx.VERTICAL )

		self.m_staticText30 = wx.StaticText( self, wx.ID_ANY, u"Creation Tools", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText30.Wrap( -1 )

		self.m_staticText30.Enable( False )

		bSizer19.Add( self.m_staticText30, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_button32 = wx.Button( self, wx.ID_ANY, u"Add Folder...", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer19.Add( self.m_button32, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_button10 = wx.Button( self, wx.ID_ANY, u"Add File...", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer19.Add( self.m_button10, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_button101 = wx.Button( self, wx.ID_ANY, u"Copy file...", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer19.Add( self.m_button101, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_button11 = wx.Button( self, wx.ID_ANY, u"Delete", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer19.Add( self.m_button11, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_staticline8 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer19.Add( self.m_staticline8, 0, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )

		self.m_staticText31 = wx.StaticText( self, wx.ID_ANY, u"Filesystem Tools", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText31.Wrap( -1 )

		self.m_staticText31.Enable( False )

		bSizer19.Add( self.m_staticText31, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_button1011 = wx.Button( self, wx.ID_ANY, u"Compress", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer19.Add( self.m_button1011, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_button1012 = wx.Button( self, wx.ID_ANY, u"Decompress", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer19.Add( self.m_button1012, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_button10121 = wx.Button( self, wx.ID_ANY, u"Extract", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer19.Add( self.m_button10121, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer19.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_staticText311 = wx.StaticText( self, wx.ID_ANY, u"UNSAFE", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText311.Wrap( -1 )

		self.m_staticText311.Enable( False )

		bSizer19.Add( self.m_staticText311, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )


		bSizer18.Add( bSizer19, 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer18 )
		self.Layout()

	def __del__( self ):
		pass


###########################################################################
## Class templatePanelDoNotDelete
###########################################################################

class templatePanelDoNotDelete ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 640,640 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		self.SetMinSize( wx.Size( 480,480 ) )


	def __del__( self ):
		pass


###########################################################################
## Class editorRoom
###########################################################################

class editorRoom ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 830,640 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_MENU ) )
		self.SetMinSize( wx.Size( 480,480 ) )

		bSizer78 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer80 = wx.BoxSizer( wx.VERTICAL )

		self.btnRoomCreateNew = wx.Button( self, wx.ID_ANY, u"Create new...", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.btnRoomCreateNew.Enable( False )

		bSizer80.Add( self.btnRoomCreateNew, 0, wx.ALL|wx.EXPAND, 5 )

		self.btnRoomDelete = wx.Button( self, wx.ID_ANY, u"Delete", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.btnRoomDelete.Enable( False )

		bSizer80.Add( self.btnRoomDelete, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_button80 = wx.Button( self, wx.ID_ANY, u"Duplicate", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_button80.Enable( False )

		bSizer80.Add( self.m_button80, 0, wx.ALL|wx.EXPAND, 5 )

		self.checkRoomApplyToAll = wx.CheckBox( self, wx.ID_ANY, u"Apply to all", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkRoomApplyToAll.Enable( False )

		bSizer80.Add( self.checkRoomApplyToAll, 0, wx.ALL, 5 )

		self.m_staticline241 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer80.Add( self.m_staticline241, 0, wx.EXPAND |wx.ALL, 5 )

		self.m_button81 = wx.Button( self, wx.ID_ANY, u"Transfer...", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_button81.Enable( False )
		self.m_button81.SetToolTip( u"Copies some or all of the properties of the selected item into another. Useful for making entries identical when \"Apply to all\" has stopped recognising duplicates." )

		bSizer80.Add( self.m_button81, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_button82 = wx.Button( self, wx.ID_ANY, u"Move Down", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_button82.Enable( False )

		bSizer80.Add( self.m_button82, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_button83 = wx.Button( self, wx.ID_ANY, u"Move Up", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_button83.Enable( False )

		bSizer80.Add( self.m_button83, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_staticline2411 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer80.Add( self.m_staticline2411, 0, wx.EXPAND |wx.ALL, 5 )

		self.btnRoomLoadPreview = wx.Button( self, wx.ID_ANY, u"Start Preview", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.btnRoomLoadPreview.Enable( False )

		bSizer80.Add( self.btnRoomLoadPreview, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer78.Add( bSizer80, 0, wx.EXPAND, 5 )

		bSizer68 = wx.BoxSizer( wx.VERTICAL )

		bSizer81 = wx.BoxSizer( wx.HORIZONTAL )

		sbSizer28 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Room Parameters" ), wx.VERTICAL )

		self.treeParam = wx.TreeCtrl( sbSizer28.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT )
		sbSizer28.Add( self.treeParam, 1, wx.EXPAND|wx.ALL, 5 )


		bSizer81.Add( sbSizer28, 2, wx.EXPAND|wx.TOP|wx.BOTTOM|wx.RIGHT, 5 )

		sbSizer29 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Room States and Progression" ), wx.VERTICAL )

		sbSizer29.SetMinSize( wx.Size( 288,-1 ) )
		self.treeStateProgression = wx.TreeCtrl( sbSizer29.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT )
		sbSizer29.Add( self.treeStateProgression, 1, wx.ALL|wx.EXPAND, 5 )

		wSizer8 = wx.WrapSizer( wx.HORIZONTAL, 0 )

		self.btnAddState = wx.Button( sbSizer29.GetStaticBox(), wx.ID_ANY, u"Add state...", wx.DefaultPosition, wx.DefaultSize, 0 )
		wSizer8.Add( self.btnAddState, 1, wx.ALL|wx.EXPAND, 5 )

		self.btnDuplicate = wx.Button( sbSizer29.GetStaticBox(), wx.ID_ANY, u"Duplicate Below", wx.DefaultPosition, wx.DefaultSize, 0 )
		wSizer8.Add( self.btnDuplicate, 1, wx.ALL|wx.EXPAND, 5 )

		self.btnMoveUp = wx.Button( sbSizer29.GetStaticBox(), wx.ID_ANY, u"Move Up", wx.DefaultPosition, wx.DefaultSize, 0 )
		wSizer8.Add( self.btnMoveUp, 1, wx.ALL|wx.EXPAND, 5 )

		self.btnMoveDown = wx.Button( sbSizer29.GetStaticBox(), wx.ID_ANY, u"Move Down", wx.DefaultPosition, wx.DefaultSize, 0 )
		wSizer8.Add( self.btnMoveDown, 1, wx.ALL|wx.EXPAND, 5 )

		self.btnDelete = wx.Button( sbSizer29.GetStaticBox(), wx.ID_ANY, u"Delete", wx.DefaultPosition, wx.DefaultSize, 0 )
		wSizer8.Add( self.btnDelete, 1, wx.ALL|wx.EXPAND, 5 )

		self.btnAddCondition = wx.Button( sbSizer29.GetStaticBox(), wx.ID_ANY, u"Add condition...", wx.DefaultPosition, wx.DefaultSize, 0 )
		wSizer8.Add( self.btnAddCondition, 1, wx.ALL|wx.EXPAND, 5 )

		self.btnEditChapter = wx.Button( sbSizer29.GetStaticBox(), wx.ID_ANY, u"Change chapters...", wx.DefaultPosition, wx.DefaultSize, 0 )
		wSizer8.Add( self.btnEditChapter, 1, wx.ALL|wx.EXPAND, 5 )


		sbSizer29.Add( wSizer8, 0, wx.EXPAND, 5 )


		bSizer81.Add( sbSizer29, 1, wx.EXPAND|wx.TOP|wx.BOTTOM|wx.LEFT, 5 )


		bSizer68.Add( bSizer81, 1, wx.EXPAND, 5 )

		sbSizer30 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Static Environment Preview" ), wx.VERTICAL )

		bSizer82 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer82.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.bitmapRoomTop = wx.StaticBitmap( sbSizer30.GetStaticBox(), wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 256,192 ), 0 )
		bSizer82.Add( self.bitmapRoomTop, 0, wx.ALL, 5 )


		bSizer82.Add( ( 10, 0), 1, wx.EXPAND, 5 )

		self.bitmapRoomBottom = wx.StaticBitmap( sbSizer30.GetStaticBox(), wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 256,192 ), 0 )
		bSizer82.Add( self.bitmapRoomBottom, 0, wx.ALL, 5 )


		bSizer82.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		sbSizer30.Add( bSizer82, 0, 0, 5 )

		bSizer83 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer88 = wx.BoxSizer( wx.VERTICAL )

		self.checkboxShowHitbox = wx.CheckBox( sbSizer30.GetStaticBox(), wx.ID_ANY, u"Show all hitboxes", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkboxShowHitbox.SetValue(True)
		bSizer88.Add( self.checkboxShowHitbox, 0, wx.ALL, 5 )

		self.checkAlphaFillHitbox = wx.CheckBox( sbSizer30.GetStaticBox(), wx.ID_ANY, u"Shade all hitboxes", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer88.Add( self.checkAlphaFillHitbox, 0, wx.ALL, 5 )

		self.checkboxShowInterface = wx.CheckBox( sbSizer30.GetStaticBox(), wx.ID_ANY, u"Simulate movemode hitboxes", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer88.Add( self.checkboxShowInterface, 0, wx.ALL, 5 )


		bSizer83.Add( bSizer88, 0, wx.EXPAND, 5 )


		bSizer83.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_staticText47 = wx.StaticText( sbSizer30.GetStaticBox(), wx.ID_ANY, u"Double-click the image to change the background", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText47.Wrap( -1 )

		self.m_staticText47.Enable( False )

		bSizer83.Add( self.m_staticText47, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )


		sbSizer30.Add( bSizer83, 0, wx.EXPAND, 5 )


		bSizer68.Add( sbSizer30, 0, wx.ALIGN_CENTER_HORIZONTAL, 5 )


		bSizer78.Add( bSizer68, 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer78 )
		self.Layout()

		# Connect Events
		self.btnRoomCreateNew.Bind( wx.EVT_BUTTON, self.btnRoomCreateNewOnButtonClick )
		self.btnRoomDelete.Bind( wx.EVT_BUTTON, self.btnRoomDeleteOnButtonClick )
		self.btnRoomLoadPreview.Bind( wx.EVT_BUTTON, self.btnRoomLoadPreviewOnButtonClick )
		self.treeParam.Bind( wx.EVT_TREE_ITEM_ACTIVATED, self.treeParamOnTreeItemActivated )
		self.treeParam.Bind( wx.EVT_TREE_SEL_CHANGED, self.treeParamOnTreeSelChanged )
		self.treeStateProgression.Bind( wx.EVT_TREE_ITEM_ACTIVATED, self.treeStateProgressionOnTreeItemActivated )
		self.treeStateProgression.Bind( wx.EVT_TREE_SEL_CHANGED, self.treeStateProgressionOnTreeSelChanged )
		self.btnAddState.Bind( wx.EVT_BUTTON, self.btnAddStateOnButtonClick )
		self.btnDuplicate.Bind( wx.EVT_BUTTON, self.btnDuplicateOnButtonClick )
		self.btnMoveUp.Bind( wx.EVT_BUTTON, self.btnMoveUpOnButtonClick )
		self.btnMoveDown.Bind( wx.EVT_BUTTON, self.btnMoveDownOnButtonClick )
		self.btnDelete.Bind( wx.EVT_BUTTON, self.btnDeleteOnButtonClick )
		self.btnAddCondition.Bind( wx.EVT_BUTTON, self.btnAddConditionOnButtonClick )
		self.btnEditChapter.Bind( wx.EVT_BUTTON, self.btnEditChapterOnButtonClick )
		self.bitmapRoomTop.Bind( wx.EVT_LEFT_DCLICK, self.bitmapRoomTopOnLeftDClick )
		self.bitmapRoomBottom.Bind( wx.EVT_LEFT_DCLICK, self.bitmapRoomBottomOnLeftDClick )
		self.checkboxShowHitbox.Bind( wx.EVT_CHECKBOX, self.checkboxShowHitboxOnCheckBox )
		self.checkAlphaFillHitbox.Bind( wx.EVT_CHECKBOX, self.checkAlphaFillHitboxOnCheckBox )
		self.checkboxShowInterface.Bind( wx.EVT_CHECKBOX, self.checkboxShowInterfaceOnCheckBox )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def btnRoomCreateNewOnButtonClick( self, event ):
		event.Skip()

	def btnRoomDeleteOnButtonClick( self, event ):
		event.Skip()

	def btnRoomLoadPreviewOnButtonClick( self, event ):
		event.Skip()

	def treeParamOnTreeItemActivated( self, event ):
		event.Skip()

	def treeParamOnTreeSelChanged( self, event ):
		event.Skip()

	def treeStateProgressionOnTreeItemActivated( self, event ):
		event.Skip()

	def treeStateProgressionOnTreeSelChanged( self, event ):
		event.Skip()

	def btnAddStateOnButtonClick( self, event ):
		event.Skip()

	def btnDuplicateOnButtonClick( self, event ):
		event.Skip()

	def btnMoveUpOnButtonClick( self, event ):
		event.Skip()

	def btnMoveDownOnButtonClick( self, event ):
		event.Skip()

	def btnDeleteOnButtonClick( self, event ):
		event.Skip()

	def btnAddConditionOnButtonClick( self, event ):
		event.Skip()

	def btnEditChapterOnButtonClick( self, event ):
		event.Skip()

	def bitmapRoomTopOnLeftDClick( self, event ):
		event.Skip()

	def bitmapRoomBottomOnLeftDClick( self, event ):
		event.Skip()

	def checkboxShowHitboxOnCheckBox( self, event ):
		event.Skip()

	def checkAlphaFillHitboxOnCheckBox( self, event ):
		event.Skip()

	def checkboxShowInterfaceOnCheckBox( self, event ):
		event.Skip()


###########################################################################
## Class templatePanelPuzzleTypeEditorDoNotDelete
###########################################################################

class templatePanelPuzzleTypeEditorDoNotDelete ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 600,600 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		self.SetMinSize( wx.Size( 440,440 ) )


	def __del__( self ):
		pass


###########################################################################
## Class editorScript
###########################################################################

class editorScript ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 640,640 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_MENU ) )
		self.SetMinSize( wx.Size( 480,480 ) )

		bSizer37 = wx.BoxSizer( wx.HORIZONTAL )

		sizerScriptingTools = wx.BoxSizer( wx.VERTICAL )

		bSizer42 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText23 = wx.StaticText( self, wx.ID_ANY, u"Context:", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText23.Wrap( -1 )

		self.m_staticText23.Enable( False )
		self.m_staticText23.SetToolTip( u"The context defines how the script will be executed, and restricts the possible operations it can run." )

		bSizer42.Add( self.m_staticText23, 0, wx.ALL, 5 )

		self.textScriptingContext = wx.StaticText( self, wx.ID_ANY, u"Primitive", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.textScriptingContext.Wrap( -1 )

		self.textScriptingContext.Enable( False )

		bSizer42.Add( self.textScriptingContext, 1, wx.ALL, 5 )


		sizerScriptingTools.Add( bSizer42, 0, wx.EXPAND, 5 )

		self.staticTextBranchingWarning = wx.StaticText( self, wx.ID_ANY, u"Conditional behaviour must be changed from the Event Overview.", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL )
		self.staticTextBranchingWarning.Wrap( 200 )

		self.staticTextBranchingWarning.Enable( False )

		sizerScriptingTools.Add( self.staticTextBranchingWarning, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		sbSizer8 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Scripting" ), wx.VERTICAL )

		wSizer2 = wx.WrapSizer( wx.HORIZONTAL, 0 )

		self.buttonInsertBelow = wx.Button( sbSizer8.GetStaticBox(), wx.ID_ANY, u"Add Below...", wx.DefaultPosition, wx.DefaultSize, 0 )
		wSizer2.Add( self.buttonInsertBelow, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5 )

		self.buttonInsertAbove = wx.Button( sbSizer8.GetStaticBox(), wx.ID_ANY, u"Add Above...", wx.DefaultPosition, wx.DefaultSize, 0 )
		wSizer2.Add( self.buttonInsertAbove, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5 )

		self.buttonMoveUp = wx.Button( sbSizer8.GetStaticBox(), wx.ID_ANY, u"Move Up", wx.DefaultPosition, wx.DefaultSize, 0 )
		wSizer2.Add( self.buttonMoveUp, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5 )

		self.buttonMoveDown = wx.Button( sbSizer8.GetStaticBox(), wx.ID_ANY, u"Move Down", wx.DefaultPosition, wx.DefaultSize, 0 )
		wSizer2.Add( self.buttonMoveDown, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5 )

		self.buttonCopy = wx.Button( sbSizer8.GetStaticBox(), wx.ID_ANY, u"Duplicate", wx.DefaultPosition, wx.DefaultSize, 0 )
		wSizer2.Add( self.buttonCopy, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5 )

		self.buttonDeleteInstruction = wx.Button( sbSizer8.GetStaticBox(), wx.ID_ANY, u"Delete", wx.DefaultPosition, wx.DefaultSize, 0 )
		wSizer2.Add( self.buttonDeleteInstruction, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5 )

		self.btnExpandAll = wx.Button( sbSizer8.GetStaticBox(), wx.ID_ANY, u"Expand All", wx.DefaultPosition, wx.DefaultSize, 0 )
		wSizer2.Add( self.btnExpandAll, 1, wx.TOP|wx.RIGHT|wx.LEFT|wx.EXPAND, 5 )

		self.btnCollapseAll = wx.Button( sbSizer8.GetStaticBox(), wx.ID_ANY, u"Collapse All", wx.DefaultPosition, wx.DefaultSize, 0 )
		wSizer2.Add( self.btnCollapseAll, 1, wx.TOP|wx.RIGHT|wx.LEFT|wx.EXPAND, 5 )


		sbSizer8.Add( wSizer2, 0, wx.EXPAND, 5 )


		sizerScriptingTools.Add( sbSizer8, 0, wx.BOTTOM|wx.EXPAND, 5 )

		sbSizer81 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Finalizing" ), wx.VERTICAL )

		wSizer21 = wx.WrapSizer( wx.HORIZONTAL, 0 )

		self.buttonTriggerWidebrimSync = wx.Button( sbSizer81.GetStaticBox(), wx.ID_ANY, u"Preview", wx.DefaultPosition, wx.DefaultSize, 0 )
		wSizer21.Add( self.buttonTriggerWidebrimSync, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5 )

		self.buttonManualVerify = wx.Button( sbSizer81.GetStaticBox(), wx.ID_ANY, u"Verify...", wx.DefaultPosition, wx.DefaultSize, 0 )
		wSizer21.Add( self.buttonManualVerify, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5 )


		sbSizer81.Add( wSizer21, 0, wx.EXPAND, 5 )


		sizerScriptingTools.Add( sbSizer81, 0, wx.BOTTOM|wx.EXPAND|wx.TOP, 5 )

		self.panelStateControls = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		sbSizer9 = wx.StaticBoxSizer( wx.StaticBox( self.panelStateControls, wx.ID_ANY, u"State" ), wx.VERTICAL )

		self.btnGoalText = wx.Button( sbSizer9.GetStaticBox(), wx.ID_ANY, u"Setup objective text...", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer9.Add( self.btnGoalText, 0, wx.ALL|wx.EXPAND, 5 )

		self.btnBgm = wx.Button( sbSizer9.GetStaticBox(), wx.ID_ANY, u"Setup background music...", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer9.Add( self.btnBgm, 0, wx.ALL|wx.EXPAND, 5 )

		self.btnTrackState = wx.Button( sbSizer9.GetStaticBox(), wx.ID_ANY, u"Enable progression tracking...", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer9.Add( self.btnTrackState, 0, wx.ALL|wx.EXPAND, 5 )


		self.panelStateControls.SetSizer( sbSizer9 )
		self.panelStateControls.Layout()
		sbSizer9.Fit( self.panelStateControls )
		sizerScriptingTools.Add( self.panelStateControls, 0, wx.BOTTOM|wx.EXPAND|wx.TOP, 5 )

		sbSizer10 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Description" ), wx.VERTICAL )

		self.textDescription = wx.TextCtrl( sbSizer10.GetStaticBox(), wx.ID_ANY, u"Select an instruction to get a description...", wx.DefaultPosition, wx.DefaultSize, wx.TE_BESTWRAP|wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_WORDWRAP|wx.BORDER_NONE )
		self.textDescription.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_MENU ) )
		self.textDescription.Enable( False )

		sbSizer10.Add( self.textDescription, 1, wx.ALL|wx.EXPAND, 5 )


		sizerScriptingTools.Add( sbSizer10, 1, wx.EXPAND|wx.TOP, 5 )


		bSizer37.Add( sizerScriptingTools, 1, wx.EXPAND, 5 )

		self.panelScripting = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		sizerScriptingEditor = wx.BoxSizer( wx.VERTICAL )

		bSizer52 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText31 = wx.StaticText( self.panelScripting, wx.ID_ANY, u"Script View", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText31.Wrap( -1 )

		self.m_staticText31.Enable( False )

		bSizer52.Add( self.m_staticText31, 0, wx.LEFT|wx.TOP, 5 )


		bSizer52.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_staticText32 = wx.StaticText( self.panelScripting, wx.ID_ANY, u"Click to get description, double-click to edit", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText32.Wrap( -1 )

		self.m_staticText32.Enable( False )

		bSizer52.Add( self.m_staticText32, 0, wx.RIGHT|wx.TOP, 5 )


		sizerScriptingEditor.Add( bSizer52, 0, wx.EXPAND, 5 )

		self.treeScript = wx.TreeCtrl( self.panelScripting, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TR_DEFAULT_STYLE|wx.TR_FULL_ROW_HIGHLIGHT|wx.TR_HIDE_ROOT|wx.TR_NO_LINES|wx.TR_TWIST_BUTTONS )
		sizerScriptingEditor.Add( self.treeScript, 2, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )

		self.paneCharacters = wx.CollapsiblePane( self.panelScripting, wx.ID_ANY, u"Edit Characters...", wx.DefaultPosition, wx.DefaultSize, wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE )
		self.paneCharacters.Collapse( False )

		bSizer43 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer45 = wx.BoxSizer( wx.VERTICAL )

		listAllCharactersChoices = []
		self.listAllCharacters = wx.ListBox( self.paneCharacters.GetPane(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, listAllCharactersChoices, 0 )
		bSizer45.Add( self.listAllCharacters, 1, wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )

		wSizer1 = wx.WrapSizer( wx.HORIZONTAL, 0 )

		self.btnCharMoveUp = wx.Button( self.paneCharacters.GetPane(), wx.ID_ANY, u"Up", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.btnCharMoveUp.SetMinSize( wx.Size( 40,-1 ) )

		wSizer1.Add( self.btnCharMoveUp, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5 )

		self.btnCharMoveDown = wx.Button( self.paneCharacters.GetPane(), wx.ID_ANY, u"Down", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.btnCharMoveDown.SetMinSize( wx.Size( 40,-1 ) )

		wSizer1.Add( self.btnCharMoveDown, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5 )

		self.btnAddNewCharacter = wx.Button( self.paneCharacters.GetPane(), wx.ID_ANY, u"Add...", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.btnAddNewCharacter.SetMinSize( wx.Size( 55,-1 ) )

		wSizer1.Add( self.btnAddNewCharacter, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5 )

		self.btnDeleteSelectedCharacter = wx.Button( self.paneCharacters.GetPane(), wx.ID_ANY, u"Delete", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.btnDeleteSelectedCharacter.SetMinSize( wx.Size( 55,-1 ) )

		wSizer1.Add( self.btnDeleteSelectedCharacter, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5 )

		self.btnReplaceCharacter = wx.Button( self.paneCharacters.GetPane(), wx.ID_ANY, u"Replace...", wx.DefaultPosition, wx.DefaultSize, 0 )
		wSizer1.Add( self.btnReplaceCharacter, 1, wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, 5 )


		bSizer45.Add( wSizer1, 0, wx.EXPAND, 5 )


		bSizer43.Add( bSizer45, 1, wx.EXPAND, 5 )

		bSizer46 = wx.BoxSizer( wx.VERTICAL )

		sbSizer11 = wx.StaticBoxSizer( wx.StaticBox( self.paneCharacters.GetPane(), wx.ID_ANY, u"Parameters" ), wx.VERTICAL )

		bSizer47 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText27 = wx.StaticText( sbSizer11.GetStaticBox(), wx.ID_ANY, u"Starting Animation", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText27.Wrap( -1 )

		self.m_staticText27.SetMinSize( wx.Size( 100,-1 ) )

		bSizer47.Add( self.m_staticText27, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		choiceCharacterAnimStartChoices = []
		self.choiceCharacterAnimStart = wx.Choice( sbSizer11.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choiceCharacterAnimStartChoices, 0 )
		self.choiceCharacterAnimStart.SetSelection( 0 )
		bSizer47.Add( self.choiceCharacterAnimStart, 1, wx.ALL, 5 )


		sbSizer11.Add( bSizer47, 0, wx.EXPAND, 5 )

		bSizer471 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText271 = wx.StaticText( sbSizer11.GetStaticBox(), wx.ID_ANY, u"Starting Position", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText271.Wrap( -1 )

		self.m_staticText271.SetMinSize( wx.Size( 100,-1 ) )

		bSizer471.Add( self.m_staticText271, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		choiceCharacterSlotChoices = [ u"Default left", u"Left pair, left side", u"Left pair, right side", u"Default middle", u"Default right", u"Right pair, left side", u"Right pair, right side", u"INVALID (middle)" ]
		self.choiceCharacterSlot = wx.Choice( sbSizer11.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choiceCharacterSlotChoices, 0 )
		self.choiceCharacterSlot.SetSelection( 0 )
		bSizer471.Add( self.choiceCharacterSlot, 1, wx.ALL, 5 )


		sbSizer11.Add( bSizer471, 0, wx.EXPAND, 5 )

		self.checkDisableCharacterVisibility = wx.CheckBox( sbSizer11.GetStaticBox(), wx.ID_ANY, u"Hide character at start", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer11.Add( self.checkDisableCharacterVisibility, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.checkDisableBadAnims = wx.CheckBox( sbSizer11.GetStaticBox(), wx.ID_ANY, u"Hide unintentional animations", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.checkDisableBadAnims.SetValue(True)
		sbSizer11.Add( self.checkDisableBadAnims, 0, wx.ALIGN_CENTER|wx.ALL, 5 )


		bSizer46.Add( sbSizer11, 0, wx.EXPAND, 5 )

		sbSizer12 = wx.StaticBoxSizer( wx.StaticBox( self.paneCharacters.GetPane(), wx.ID_ANY, u"Character Starting Preview" ), wx.VERTICAL )

		self.bitmapRenderCharacterPreview = wx.StaticBitmap( sbSizer12.GetStaticBox(), wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.bitmapRenderCharacterPreview.SetMinSize( wx.Size( 256,192 ) )

		sbSizer12.Add( self.bitmapRenderCharacterPreview, 0, wx.ALIGN_CENTER|wx.ALL, 5 )


		bSizer46.Add( sbSizer12, 0, wx.EXPAND, 5 )


		bSizer43.Add( bSizer46, 0, wx.EXPAND, 5 )


		self.paneCharacters.GetPane().SetSizer( bSizer43 )
		self.paneCharacters.GetPane().Layout()
		bSizer43.Fit( self.paneCharacters.GetPane() )
		sizerScriptingEditor.Add( self.paneCharacters, 0, wx.EXPAND |wx.ALL, 5 )


		self.panelScripting.SetSizer( sizerScriptingEditor )
		self.panelScripting.Layout()
		sizerScriptingEditor.Fit( self.panelScripting )
		bSizer37.Add( self.panelScripting, 5, wx.EXPAND |wx.ALL, 0 )


		self.SetSizer( bSizer37 )
		self.Layout()

		# Connect Events
		self.buttonInsertBelow.Bind( wx.EVT_BUTTON, self.buttonInsertBelowOnButtonClick )
		self.buttonInsertAbove.Bind( wx.EVT_BUTTON, self.buttonInsertAboveOnButtonClick )
		self.buttonMoveUp.Bind( wx.EVT_BUTTON, self.buttonMoveUpOnButtonClick )
		self.buttonMoveDown.Bind( wx.EVT_BUTTON, self.buttonMoveDownOnButtonClick )
		self.buttonCopy.Bind( wx.EVT_BUTTON, self.buttonCopyOnButtonClick )
		self.buttonDeleteInstruction.Bind( wx.EVT_BUTTON, self.buttonDeleteInstructionOnButtonClick )
		self.btnExpandAll.Bind( wx.EVT_BUTTON, self.btnExpandAllOnButtonClick )
		self.btnCollapseAll.Bind( wx.EVT_BUTTON, self.btnCollapseAllOnButtonClick )
		self.buttonTriggerWidebrimSync.Bind( wx.EVT_BUTTON, self.buttonTriggerWidebrimSyncOnButtonClick )
		self.buttonManualVerify.Bind( wx.EVT_BUTTON, self.buttonManualVerifyOnButtonClick )
		self.btnGoalText.Bind( wx.EVT_BUTTON, self.btnGoalTextOnButtonClick )
		self.btnBgm.Bind( wx.EVT_BUTTON, self.btnBgmOnButtonClick )
		self.btnTrackState.Bind( wx.EVT_BUTTON, self.btnTrackStateOnButtonClick )
		self.treeScript.Bind( wx.EVT_TREE_ITEM_ACTIVATED, self.treeScriptOnTreeItemActivated )
		self.treeScript.Bind( wx.EVT_TREE_SEL_CHANGED, self.treeScriptOnTreeSelChanged )
		self.paneCharacters.Bind( wx.EVT_COLLAPSIBLEPANE_CHANGED, self.paneCharactersOnCollapsiblePaneChanged )
		self.listAllCharacters.Bind( wx.EVT_LISTBOX, self.listAllCharactersOnListBox )
		self.listAllCharacters.Bind( wx.EVT_LISTBOX_DCLICK, self.listAllCharactersOnListBoxDClick )
		self.btnCharMoveUp.Bind( wx.EVT_BUTTON, self.btnCharMoveUpOnButtonClick )
		self.btnCharMoveDown.Bind( wx.EVT_BUTTON, self.btnCharMoveDownOnButtonClick )
		self.btnAddNewCharacter.Bind( wx.EVT_BUTTON, self.btnAddNewCharacterOnButtonClick )
		self.btnDeleteSelectedCharacter.Bind( wx.EVT_BUTTON, self.btnDeleteSelectedCharacterOnButtonClick )
		self.btnReplaceCharacter.Bind( wx.EVT_BUTTON, self.btnReplaceCharacterOnButtonClick )
		self.choiceCharacterAnimStart.Bind( wx.EVT_CHOICE, self.choiceCharacterAnimStartOnChoice )
		self.choiceCharacterSlot.Bind( wx.EVT_CHOICE, self.choiceCharacterSlotOnChoice )
		self.checkDisableCharacterVisibility.Bind( wx.EVT_CHECKBOX, self.checkDisableCharacterVisibilityOnCheckBox )
		self.checkDisableBadAnims.Bind( wx.EVT_CHECKBOX, self.checkDisableBadAnimsOnCheckBox )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def buttonInsertBelowOnButtonClick( self, event ):
		event.Skip()

	def buttonInsertAboveOnButtonClick( self, event ):
		event.Skip()

	def buttonMoveUpOnButtonClick( self, event ):
		event.Skip()

	def buttonMoveDownOnButtonClick( self, event ):
		event.Skip()

	def buttonCopyOnButtonClick( self, event ):
		event.Skip()

	def buttonDeleteInstructionOnButtonClick( self, event ):
		event.Skip()

	def btnExpandAllOnButtonClick( self, event ):
		event.Skip()

	def btnCollapseAllOnButtonClick( self, event ):
		event.Skip()

	def buttonTriggerWidebrimSyncOnButtonClick( self, event ):
		event.Skip()

	def buttonManualVerifyOnButtonClick( self, event ):
		event.Skip()

	def btnGoalTextOnButtonClick( self, event ):
		event.Skip()

	def btnBgmOnButtonClick( self, event ):
		event.Skip()

	def btnTrackStateOnButtonClick( self, event ):
		event.Skip()

	def treeScriptOnTreeItemActivated( self, event ):
		event.Skip()

	def treeScriptOnTreeSelChanged( self, event ):
		event.Skip()

	def paneCharactersOnCollapsiblePaneChanged( self, event ):
		event.Skip()

	def listAllCharactersOnListBox( self, event ):
		event.Skip()

	def listAllCharactersOnListBoxDClick( self, event ):
		event.Skip()

	def btnCharMoveUpOnButtonClick( self, event ):
		event.Skip()

	def btnCharMoveDownOnButtonClick( self, event ):
		event.Skip()

	def btnAddNewCharacterOnButtonClick( self, event ):
		event.Skip()

	def btnDeleteSelectedCharacterOnButtonClick( self, event ):
		event.Skip()

	def btnReplaceCharacterOnButtonClick( self, event ):
		event.Skip()

	def choiceCharacterAnimStartOnChoice( self, event ):
		event.Skip()

	def choiceCharacterSlotOnChoice( self, event ):
		event.Skip()

	def checkDisableCharacterVisibilityOnCheckBox( self, event ):
		event.Skip()

	def checkDisableBadAnimsOnCheckBox( self, event ):
		event.Skip()


###########################################################################
## Class editorPuzzle
###########################################################################

class editorPuzzle ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 640,640 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_MENU ) )
		self.SetMinSize( wx.Size( 480,480 ) )

		bSizer20 = wx.BoxSizer( wx.VERTICAL )

		self.editorScroll = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
		self.editorScroll.SetScrollRate( 5, 5 )
		editorMainSizer = wx.BoxSizer( wx.VERTICAL )

		self.paneEditParam = wx.CollapsiblePane( self.editorScroll, wx.ID_ANY, u"Puzzle Parameters", wx.DefaultPosition, wx.DefaultSize, wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE )
		self.paneEditParam.Collapse( False )

		bSizer22 = wx.BoxSizer( wx.VERTICAL )

		sizerName = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText12 = wx.StaticText( self.paneEditParam.GetPane(), wx.ID_ANY, u"Name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText12.Wrap( -1 )

		sizerName.Add( self.m_staticText12, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.puzzleName = wx.TextCtrl( self.paneEditParam.GetPane(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.puzzleName.SetMaxLength( 48 )
		sizerName.Add( self.puzzleName, 1, wx.ALL, 5 )


		bSizer22.Add( sizerName, 0, wx.EXPAND, 5 )

		sizerParams = wx.WrapSizer( wx.HORIZONTAL, 0 )

		sizerId = wx.StaticBoxSizer( wx.StaticBox( self.paneEditParam.GetPane(), wx.ID_ANY, u"IDs" ), wx.VERTICAL )


		sizerId.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		fgSizer3 = wx.FlexGridSizer( 3, 2, 0, 0 )
		fgSizer3.SetFlexibleDirection( wx.HORIZONTAL )
		fgSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_staticText241 = wx.StaticText( sizerId.GetStaticBox(), wx.ID_ANY, u"Internal", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText241.Wrap( -1 )

		self.m_staticText241.Enable( False )

		fgSizer3.Add( self.m_staticText241, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.puzzleInternalId = wx.TextCtrl( sizerId.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( -1,-1 ), wx.TE_READONLY )
		self.puzzleInternalId.SetToolTip( u"The internal ID is used for asset recognition so cannot be changed in this view. Change this from the Overview." )

		fgSizer3.Add( self.puzzleInternalId, 0, wx.ALL, 5 )

		self.m_staticText25 = wx.StaticText( sizerId.GetStaticBox(), wx.ID_ANY, u"External", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText25.Wrap( -1 )

		fgSizer3.Add( self.m_staticText25, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		puzzlePickExternalIdChoices = []
		self.puzzlePickExternalId = wx.Choice( sizerId.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), puzzlePickExternalIdChoices, 0 )
		self.puzzlePickExternalId.SetSelection( 0 )
		self.puzzlePickExternalId.SetToolTip( u"The external ID is the value shown when starting the puzzle. It's otherwise non-critical - some values change graphics. Changing this value may break progression on previous saves." )

		fgSizer3.Add( self.puzzlePickExternalId, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_staticText26 = wx.StaticText( sizerId.GetStaticBox(), wx.ID_ANY, u"Tutorial", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText26.Wrap( -1 )

		fgSizer3.Add( self.m_staticText26, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		puzzlePickTutorialIdChoices = []
		self.puzzlePickTutorialId = wx.Choice( sizerId.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), puzzlePickTutorialIdChoices, 0 )
		self.puzzlePickTutorialId.SetSelection( 0 )
		self.puzzlePickTutorialId.SetToolTip( u"If enabled, this will trigger a small sequence before the puzzle that explains how it should be solved. Recommended to enable and set to the proper tutorial for the puzzle type. Once the tutorial has played, it will not play again." )

		fgSizer3.Add( self.puzzlePickTutorialId, 1, wx.ALL|wx.EXPAND, 5 )


		sizerId.Add( fgSizer3, 0, wx.ALIGN_CENTER, 5 )


		sizerId.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		sizerParams.Add( sizerId, 2, wx.ALL|wx.EXPAND, 5 )

		sizerPicarats = wx.StaticBoxSizer( wx.StaticBox( self.paneEditParam.GetPane(), wx.ID_ANY, u"Picarats" ), wx.VERTICAL )


		sizerPicarats.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		fgSizer4 = wx.FlexGridSizer( 3, 2, 0, 0 )
		fgSizer4.SetFlexibleDirection( wx.HORIZONTAL )
		fgSizer4.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_staticText16 = wx.StaticText( sizerPicarats.GetStaticBox(), wx.ID_ANY, u"Max", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText16.Wrap( -1 )

		fgSizer4.Add( self.m_staticText16, 0, wx.ALIGN_CENTER|wx.LEFT, 5 )

		self.puzzlePicaratMax = wx.TextCtrl( sizerPicarats.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( -1,-1 ), wx.TE_CENTER )
		self.puzzlePicaratMax.SetMaxLength( 3 )
		self.puzzlePicaratMax.SetMinSize( wx.Size( 40,-1 ) )

		fgSizer4.Add( self.puzzlePicaratMax, 1, wx.ALL, 5 )


		fgSizer4.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.puzzlePicaratMid = wx.TextCtrl( sizerPicarats.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( -1,-1 ), wx.TE_CENTER )
		self.puzzlePicaratMid.SetMaxLength( 3 )
		self.puzzlePicaratMid.SetMinSize( wx.Size( 40,-1 ) )

		fgSizer4.Add( self.puzzlePicaratMid, 1, wx.ALL, 5 )

		self.m_staticText18 = wx.StaticText( sizerPicarats.GetStaticBox(), wx.ID_ANY, u"Min", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText18.Wrap( -1 )

		fgSizer4.Add( self.m_staticText18, 0, wx.ALIGN_CENTER|wx.LEFT, 5 )

		self.puzzlePicaratMin = wx.TextCtrl( sizerPicarats.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( -1,-1 ), wx.TE_CENTER )
		self.puzzlePicaratMin.SetMaxLength( 3 )
		self.puzzlePicaratMin.SetMinSize( wx.Size( 40,-1 ) )

		fgSizer4.Add( self.puzzlePicaratMin, 1, wx.ALL, 5 )


		sizerPicarats.Add( fgSizer4, 0, wx.ALIGN_CENTER, 5 )


		sizerPicarats.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		sizerParams.Add( sizerPicarats, 1, wx.ALL|wx.EXPAND, 5 )

		sizerSettings = wx.StaticBoxSizer( wx.StaticBox( self.paneEditParam.GetPane(), wx.ID_ANY, u"Settings" ), wx.VERTICAL )

		bSizer57 = wx.BoxSizer( wx.VERTICAL )

		fgSizer5 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer5.SetFlexibleDirection( wx.BOTH )
		fgSizer5.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_staticText28 = wx.StaticText( sizerSettings.GetStaticBox(), wx.ID_ANY, u"Reward", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText28.Wrap( -1 )

		fgSizer5.Add( self.m_staticText28, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		choiceRewardChoices = []
		self.choiceReward = wx.Choice( sizerSettings.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choiceRewardChoices, 0 )
		self.choiceReward.SetSelection( 0 )
		fgSizer5.Add( self.choiceReward, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_staticText24 = wx.StaticText( sizerSettings.GetStaticBox(), wx.ID_ANY, u"Place", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText24.Wrap( -1 )

		fgSizer5.Add( self.m_staticText24, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		choicePlaceChoices = []
		self.choicePlace = wx.Choice( sizerSettings.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choicePlaceChoices, 0 )
		self.choicePlace.SetSelection( 0 )
		fgSizer5.Add( self.choicePlace, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_staticText29 = wx.StaticText( sizerSettings.GetStaticBox(), wx.ID_ANY, u"Group", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText29.Wrap( -1 )

		fgSizer5.Add( self.m_staticText29, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		choiceGroupChoices = []
		self.choiceGroup = wx.Choice( sizerSettings.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choiceGroupChoices, 0 )
		self.choiceGroup.SetSelection( 0 )
		fgSizer5.Add( self.choiceGroup, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer57.Add( fgSizer5, 1, wx.ALIGN_CENTER, 5 )

		sbSizer7 = wx.StaticBoxSizer( wx.StaticBox( sizerSettings.GetStaticBox(), wx.ID_ANY, u"Solver" ), wx.HORIZONTAL )

		self.useAltCharacter = wx.CheckBox( sbSizer7.GetStaticBox(), wx.ID_ANY, u"Use alt character", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer7.Add( self.useAltCharacter, 1, wx.ALL, 5 )

		self.useAltVoice = wx.CheckBox( sbSizer7.GetStaticBox(), wx.ID_ANY, u"Use alt character voice", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer7.Add( self.useAltVoice, 1, wx.ALL, 5 )


		bSizer57.Add( sbSizer7, 0, wx.EXPAND, 5 )


		sizerSettings.Add( bSizer57, 1, wx.EXPAND, 5 )


		sizerParams.Add( sizerSettings, 4, wx.ALL|wx.EXPAND, 5 )


		bSizer22.Add( sizerParams, 1, wx.EXPAND, 5 )


		self.paneEditParam.GetPane().SetSizer( bSizer22 )
		self.paneEditParam.GetPane().Layout()
		bSizer22.Fit( self.paneEditParam.GetPane() )
		editorMainSizer.Add( self.paneEditParam, 0, wx.EXPAND |wx.ALL, 5 )

		self.m_staticline6 = wx.StaticLine( self.editorScroll, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		editorMainSizer.Add( self.m_staticline6, 0, wx.EXPAND, 5 )

		self.paneEditText = wx.CollapsiblePane( self.editorScroll, wx.ID_ANY, u"Text", wx.DefaultPosition, wx.DefaultSize, wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE )
		self.paneEditText.Collapse( True )

		bSizer23 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer23.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_panel9 = wx.Panel( self.paneEditText.GetPane(), wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.TAB_TRAVERSAL )
		self.m_panel9.SetMinSize( wx.Size( 440,-1 ) )
		self.m_panel9.SetMaxSize( wx.Size( 540,-1 ) )

		bSizer52 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer26 = wx.BoxSizer( wx.VERTICAL )

		bSizer25 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText19 = wx.StaticText( self.m_panel9, wx.ID_ANY, u"Preview", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText19.Wrap( -1 )

		bSizer25.Add( self.m_staticText19, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		textSelectChoiceChoices = [ u"Hint 1", u"Hint 2", u"Hint 3", u"Prompt", u"On Failed", u"On Solved" ]
		self.textSelectChoice = wx.Choice( self.m_panel9, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, textSelectChoiceChoices, 0 )
		self.textSelectChoice.SetSelection( 3 )
		bSizer25.Add( self.textSelectChoice, 1, wx.ALL, 5 )


		bSizer26.Add( bSizer25, 0, wx.EXPAND, 5 )

		self.textEdit = wx.TextCtrl( self.m_panel9, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_DONTWRAP|wx.TE_MULTILINE )
		bSizer26.Add( self.textEdit, 1, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )


		bSizer52.Add( bSizer26, 1, wx.EXPAND, 5 )

		self.hintPreview = wx.StaticBitmap( self.m_panel9, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 256,192 ), 0 )
		self.hintPreview.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INFOBK ) )
		self.hintPreview.SetMinSize( wx.Size( 256,192 ) )
		self.hintPreview.SetMaxSize( wx.Size( 256,192 ) )

		bSizer52.Add( self.hintPreview, 0, wx.ALL, 5 )


		self.m_panel9.SetSizer( bSizer52 )
		self.m_panel9.Layout()
		bSizer52.Fit( self.m_panel9 )
		bSizer23.Add( self.m_panel9, 100, wx.EXPAND, 5 )


		bSizer23.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		self.paneEditText.GetPane().SetSizer( bSizer23 )
		self.paneEditText.GetPane().Layout()
		bSizer23.Fit( self.paneEditText.GetPane() )
		editorMainSizer.Add( self.paneEditText, 0, wx.EXPAND |wx.ALL, 5 )

		self.m_staticline7 = wx.StaticLine( self.editorScroll, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		editorMainSizer.Add( self.m_staticline7, 0, wx.EXPAND, 5 )

		self.paneEditBackgrounds = wx.CollapsiblePane( self.editorScroll, wx.ID_ANY, u"Backgrounds", wx.DefaultPosition, wx.DefaultSize, wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE )
		self.paneEditBackgrounds.Collapse( True )

		wSizer3 = wx.WrapSizer( wx.HORIZONTAL, wx.REMOVE_LEADING_SPACES )

		sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self.paneEditBackgrounds.GetPane(), wx.ID_ANY, u"Top Screen" ), wx.HORIZONTAL )

		self.previewBackgroundSub = wx.StaticBitmap( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 256,192 ), 0 )
		self.previewBackgroundSub.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INFOBK ) )

		sbSizer2.Add( self.previewBackgroundSub, 0, wx.ALL, 5 )

		bSizer33 = wx.BoxSizer( wx.VERTICAL )

		self.changeBackgroundSub = wx.Button( sbSizer2.GetStaticBox(), wx.ID_ANY, u"Change", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer33.Add( self.changeBackgroundSub, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_staticText27 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"Images for the top screen are presets and not unique to each puzzle. These backgrounds need to be modified within the ROM Overview.", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText27.Wrap( 160 )

		self.m_staticText27.Enable( False )

		bSizer33.Add( self.m_staticText27, 1, wx.ALIGN_CENTER|wx.ALL, 5 )


		sbSizer2.Add( bSizer33, 1, wx.EXPAND, 5 )


		wSizer3.Add( sbSizer2, 1, wx.ALL|wx.EXPAND, 5 )

		sbSizer3 = wx.StaticBoxSizer( wx.StaticBox( self.paneEditBackgrounds.GetPane(), wx.ID_ANY, u"Bottom Screen" ), wx.HORIZONTAL )

		self.previewBackgroundMain = wx.StaticBitmap( sbSizer3.GetStaticBox(), wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 256,192 ), 0 )
		self.previewBackgroundMain.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INFOBK ) )

		sbSizer3.Add( self.previewBackgroundMain, 0, wx.ALL, 5 )

		bSizer32 = wx.BoxSizer( wx.VERTICAL )

		self.changeBackgroundMain = wx.Button( sbSizer3.GetStaticBox(), wx.ID_ANY, u"Change", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer32.Add( self.changeBackgroundMain, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_checkBox1 = wx.CheckBox( sbSizer3.GetStaticBox(), wx.ID_ANY, u"Force unique image", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox1.Enable( False )
		self.m_checkBox1.SetToolTip( u"Backgrounds can be shared across different puzzles. By default, selecting an image shares the resource with its peers. Check this to create a copy of the resource for this puzzle only." )

		bSizer32.Add( self.m_checkBox1, 0, wx.ALL, 5 )

		self.m_checkBox5 = wx.CheckBox( sbSizer3.GetStaticBox(), wx.ID_ANY, u"Locale-dependent", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox5.Enable( False )
		self.m_checkBox5.SetToolTip( u"Check this if your background includes elements that may need translating depending on the player's locale. This may be greyed out if the image is a shared asset." )

		bSizer32.Add( self.m_checkBox5, 0, wx.ALL, 5 )


		sbSizer3.Add( bSizer32, 1, wx.EXPAND, 5 )


		wSizer3.Add( sbSizer3, 1, wx.ALL|wx.EXPAND, 5 )

		sbSizer31 = wx.StaticBoxSizer( wx.StaticBox( self.paneEditBackgrounds.GetPane(), wx.ID_ANY, u"Answer Screen" ), wx.HORIZONTAL )

		self.previewBackgroundAnswer = wx.StaticBitmap( sbSizer31.GetStaticBox(), wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 256,192 ), 0 )
		self.previewBackgroundAnswer.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INFOBK ) )

		sbSizer31.Add( self.previewBackgroundAnswer, 0, wx.ALL, 5 )

		bSizer321 = wx.BoxSizer( wx.VERTICAL )

		self.changeBackgroundMain1 = wx.Button( sbSizer31.GetStaticBox(), wx.ID_ANY, u"Change", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer321.Add( self.changeBackgroundMain1, 0, wx.ALL|wx.EXPAND, 5 )

		self.changeBackgroundMain11 = wx.Button( sbSizer31.GetStaticBox(), wx.ID_ANY, u"Remove", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.changeBackgroundMain11.Enable( False )
		self.changeBackgroundMain11.SetToolTip( u"Remove the selected background from the answer screen. When the puzzle is solved, the top screen image will be used instead. " )

		bSizer321.Add( self.changeBackgroundMain11, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_checkBox11 = wx.CheckBox( sbSizer31.GetStaticBox(), wx.ID_ANY, u"Force unique image", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox11.Enable( False )
		self.m_checkBox11.SetToolTip( u"Backgrounds can be shared across different puzzles. By default, selecting an image shares the resource with its peers. Check this to create a copy of the resource for this puzzle only." )

		bSizer321.Add( self.m_checkBox11, 0, wx.ALL, 5 )

		self.m_checkBox51 = wx.CheckBox( sbSizer31.GetStaticBox(), wx.ID_ANY, u"Locale-dependent", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox51.Enable( False )
		self.m_checkBox51.SetToolTip( u"Check this if your background includes elements that may need translating depending on the player's locale. This may be greyed out if the image is a shared asset." )

		bSizer321.Add( self.m_checkBox51, 0, wx.ALL, 5 )


		sbSizer31.Add( bSizer321, 1, wx.EXPAND, 5 )


		wSizer3.Add( sbSizer31, 1, wx.ALL|wx.EXPAND, 5 )


		self.paneEditBackgrounds.GetPane().SetSizer( wSizer3 )
		self.paneEditBackgrounds.GetPane().Layout()
		wSizer3.Fit( self.paneEditBackgrounds.GetPane() )
		editorMainSizer.Add( self.paneEditBackgrounds, 0, wx.EXPAND |wx.ALL, 5 )

		self.m_staticline71 = wx.StaticLine( self.editorScroll, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		editorMainSizer.Add( self.m_staticline71, 0, wx.EXPAND, 5 )

		self.paneGameplayEditor = wx.CollapsiblePane( self.editorScroll, wx.ID_ANY, u"Gameplay", wx.DefaultPosition, wx.DefaultSize, wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE )
		self.paneGameplayEditor.Collapse( True )

		sizerEdit = wx.BoxSizer( wx.VERTICAL )


		self.paneGameplayEditor.GetPane().SetSizer( sizerEdit )
		self.paneGameplayEditor.GetPane().Layout()
		sizerEdit.Fit( self.paneGameplayEditor.GetPane() )
		editorMainSizer.Add( self.paneGameplayEditor, 0, wx.EXPAND |wx.ALL, 5 )


		self.editorScroll.SetSizer( editorMainSizer )
		self.editorScroll.Layout()
		editorMainSizer.Fit( self.editorScroll )
		bSizer20.Add( self.editorScroll, 1, wx.EXPAND |wx.ALL, 5 )


		self.SetSizer( bSizer20 )
		self.Layout()

		# Connect Events
		self.Bind( wx.aui.EVT_AUI_PANE_ACTIVATED, self.editorPuzzleOnAuiPaneActivated )
		self.editorScroll.Bind( wx.EVT_SIZE, self.editorScrollOnSize )
		self.paneEditParam.Bind( wx.EVT_COLLAPSIBLEPANE_CHANGED, self.paneEditParamOnCollapsiblePaneChanged )
		self.puzzleName.Bind( wx.EVT_TEXT, self.puzzleNameOnText )
		self.puzzlePickExternalId.Bind( wx.EVT_CHOICE, self.puzzlePickExternalIdOnChoice )
		self.puzzlePickTutorialId.Bind( wx.EVT_CHOICE, self.puzzlePickTutorialIdOnChoice )
		self.puzzlePicaratMax.Bind( wx.EVT_TEXT, self.puzzlePicaratMaxOnText )
		self.puzzlePicaratMid.Bind( wx.EVT_TEXT, self.puzzlePicaratMidOnText )
		self.puzzlePicaratMin.Bind( wx.EVT_TEXT, self.puzzlePicaratMinOnText )
		self.choiceReward.Bind( wx.EVT_CHOICE, self.choiceRewardOnChoice )
		self.choicePlace.Bind( wx.EVT_CHOICE, self.choicePlaceOnChoice )
		self.choiceGroup.Bind( wx.EVT_CHOICE, self.choiceGroupOnChoice )
		self.useAltCharacter.Bind( wx.EVT_CHECKBOX, self.useAltCharacterOnCheckBox )
		self.useAltVoice.Bind( wx.EVT_CHECKBOX, self.useAltVoiceOnCheckBox )
		self.paneEditText.Bind( wx.EVT_COLLAPSIBLEPANE_CHANGED, self.paneEditTextOnCollapsiblePaneChanged )
		self.textSelectChoice.Bind( wx.EVT_CHOICE, self.textSelectChoiceOnChoice )
		self.textEdit.Bind( wx.EVT_TEXT, self.textEditOnText )
		self.paneEditBackgrounds.Bind( wx.EVT_COLLAPSIBLEPANE_CHANGED, self.paneEditBackgroundsOnCollapsiblePaneChanged )
		self.paneGameplayEditor.Bind( wx.EVT_COLLAPSIBLEPANE_CHANGED, self.paneGameplayEditorOnCollapsiblePaneChanged )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def editorPuzzleOnAuiPaneActivated( self, event ):
		event.Skip()

	def editorScrollOnSize( self, event ):
		event.Skip()

	def paneEditParamOnCollapsiblePaneChanged( self, event ):
		event.Skip()

	def puzzleNameOnText( self, event ):
		event.Skip()

	def puzzlePickExternalIdOnChoice( self, event ):
		event.Skip()

	def puzzlePickTutorialIdOnChoice( self, event ):
		event.Skip()

	def puzzlePicaratMaxOnText( self, event ):
		event.Skip()

	def puzzlePicaratMidOnText( self, event ):
		event.Skip()

	def puzzlePicaratMinOnText( self, event ):
		event.Skip()

	def choiceRewardOnChoice( self, event ):
		event.Skip()

	def choicePlaceOnChoice( self, event ):
		event.Skip()

	def choiceGroupOnChoice( self, event ):
		event.Skip()

	def useAltCharacterOnCheckBox( self, event ):
		event.Skip()

	def useAltVoiceOnCheckBox( self, event ):
		event.Skip()

	def paneEditTextOnCollapsiblePaneChanged( self, event ):
		event.Skip()

	def textSelectChoiceOnChoice( self, event ):
		event.Skip()

	def textEditOnText( self, event ):
		event.Skip()

	def paneEditBackgroundsOnCollapsiblePaneChanged( self, event ):
		event.Skip()

	def paneGameplayEditorOnCollapsiblePaneChanged( self, event ):
		event.Skip()


###########################################################################
## Class editorTraceButton
###########################################################################

class editorTraceButton ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 640,640 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_MENU ) )
		self.SetMinSize( wx.Size( 480,480 ) )

		bSizer20 = wx.BoxSizer( wx.VERTICAL )

		self.editorScroll = wx.ScrolledWindow( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.HSCROLL|wx.VSCROLL )
		self.editorScroll.SetScrollRate( 5, 5 )
		editorMainSizer = wx.BoxSizer( wx.VERTICAL )

		self.paneEditParam = wx.CollapsiblePane( self.editorScroll, wx.ID_ANY, u"Puzzle Parameters", wx.DefaultPosition, wx.DefaultSize, wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE )
		self.paneEditParam.Collapse( False )

		bSizer22 = wx.BoxSizer( wx.VERTICAL )

		sizerName = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText12 = wx.StaticText( self.paneEditParam.GetPane(), wx.ID_ANY, u"Name", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText12.Wrap( -1 )

		sizerName.Add( self.m_staticText12, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.puzzleName = wx.TextCtrl( self.paneEditParam.GetPane(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.puzzleName.SetMaxLength( 48 )
		sizerName.Add( self.puzzleName, 1, wx.ALL, 5 )


		bSizer22.Add( sizerName, 0, wx.EXPAND, 5 )

		sizerParams = wx.WrapSizer( wx.HORIZONTAL, 0 )

		sizerId = wx.StaticBoxSizer( wx.StaticBox( self.paneEditParam.GetPane(), wx.ID_ANY, u"IDs" ), wx.VERTICAL )


		sizerId.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		fgSizer3 = wx.FlexGridSizer( 3, 2, 0, 0 )
		fgSizer3.SetFlexibleDirection( wx.HORIZONTAL )
		fgSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_staticText241 = wx.StaticText( sizerId.GetStaticBox(), wx.ID_ANY, u"Internal", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText241.Wrap( -1 )

		self.m_staticText241.Enable( False )

		fgSizer3.Add( self.m_staticText241, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.puzzleInternalId = wx.TextCtrl( sizerId.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( -1,-1 ), wx.TE_READONLY )
		self.puzzleInternalId.SetToolTip( u"The internal ID is used for asset recognition so cannot be changed in this view. Change this from the Overview." )

		fgSizer3.Add( self.puzzleInternalId, 0, wx.ALL, 5 )

		self.m_staticText25 = wx.StaticText( sizerId.GetStaticBox(), wx.ID_ANY, u"External", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText25.Wrap( -1 )

		fgSizer3.Add( self.m_staticText25, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		puzzlePickExternalIdChoices = []
		self.puzzlePickExternalId = wx.Choice( sizerId.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), puzzlePickExternalIdChoices, 0 )
		self.puzzlePickExternalId.SetSelection( 0 )
		self.puzzlePickExternalId.SetToolTip( u"The external ID is the value shown when starting the puzzle. It's otherwise non-critical - some values change graphics. Changing this value may break progression on previous saves." )

		fgSizer3.Add( self.puzzlePickExternalId, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_staticText26 = wx.StaticText( sizerId.GetStaticBox(), wx.ID_ANY, u"Tutorial", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText26.Wrap( -1 )

		fgSizer3.Add( self.m_staticText26, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		puzzlePickTutorialIdChoices = []
		self.puzzlePickTutorialId = wx.Choice( sizerId.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), puzzlePickTutorialIdChoices, 0 )
		self.puzzlePickTutorialId.SetSelection( 0 )
		self.puzzlePickTutorialId.SetToolTip( u"If enabled, this will trigger a small sequence before the puzzle that explains how it should be solved. Recommended to enable and set to the proper tutorial for the puzzle type. Once the tutorial has played, it will not play again." )

		fgSizer3.Add( self.puzzlePickTutorialId, 1, wx.ALL|wx.EXPAND, 5 )


		sizerId.Add( fgSizer3, 0, wx.ALIGN_CENTER, 5 )


		sizerId.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		sizerParams.Add( sizerId, 2, wx.ALL|wx.EXPAND, 5 )

		sizerPicarats = wx.StaticBoxSizer( wx.StaticBox( self.paneEditParam.GetPane(), wx.ID_ANY, u"Picarats" ), wx.VERTICAL )


		sizerPicarats.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		fgSizer4 = wx.FlexGridSizer( 3, 2, 0, 0 )
		fgSizer4.SetFlexibleDirection( wx.HORIZONTAL )
		fgSizer4.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_staticText16 = wx.StaticText( sizerPicarats.GetStaticBox(), wx.ID_ANY, u"Max", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText16.Wrap( -1 )

		fgSizer4.Add( self.m_staticText16, 0, wx.ALIGN_CENTER|wx.LEFT, 5 )

		self.puzzlePicaratMax = wx.TextCtrl( sizerPicarats.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( -1,-1 ), wx.TE_CENTER )
		self.puzzlePicaratMax.SetMaxLength( 3 )
		self.puzzlePicaratMax.SetMinSize( wx.Size( 40,-1 ) )

		fgSizer4.Add( self.puzzlePicaratMax, 1, wx.ALL, 5 )


		fgSizer4.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.puzzlePicaratMid = wx.TextCtrl( sizerPicarats.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( -1,-1 ), wx.TE_CENTER )
		self.puzzlePicaratMid.SetMaxLength( 3 )
		self.puzzlePicaratMid.SetMinSize( wx.Size( 40,-1 ) )

		fgSizer4.Add( self.puzzlePicaratMid, 1, wx.ALL, 5 )

		self.m_staticText18 = wx.StaticText( sizerPicarats.GetStaticBox(), wx.ID_ANY, u"Min", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText18.Wrap( -1 )

		fgSizer4.Add( self.m_staticText18, 0, wx.ALIGN_CENTER|wx.LEFT, 5 )

		self.puzzlePicaratMin = wx.TextCtrl( sizerPicarats.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( -1,-1 ), wx.TE_CENTER )
		self.puzzlePicaratMin.SetMaxLength( 3 )
		self.puzzlePicaratMin.SetMinSize( wx.Size( 40,-1 ) )

		fgSizer4.Add( self.puzzlePicaratMin, 1, wx.ALL, 5 )


		sizerPicarats.Add( fgSizer4, 0, wx.ALIGN_CENTER, 5 )


		sizerPicarats.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		sizerParams.Add( sizerPicarats, 1, wx.ALL|wx.EXPAND, 5 )

		sizerSettings = wx.StaticBoxSizer( wx.StaticBox( self.paneEditParam.GetPane(), wx.ID_ANY, u"Settings" ), wx.VERTICAL )

		bSizer57 = wx.BoxSizer( wx.VERTICAL )

		fgSizer5 = wx.FlexGridSizer( 0, 2, 0, 0 )
		fgSizer5.SetFlexibleDirection( wx.BOTH )
		fgSizer5.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_staticText28 = wx.StaticText( sizerSettings.GetStaticBox(), wx.ID_ANY, u"Reward", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText28.Wrap( -1 )

		fgSizer5.Add( self.m_staticText28, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		choiceRewardChoices = []
		self.choiceReward = wx.Choice( sizerSettings.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choiceRewardChoices, 0 )
		self.choiceReward.SetSelection( 0 )
		fgSizer5.Add( self.choiceReward, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_staticText24 = wx.StaticText( sizerSettings.GetStaticBox(), wx.ID_ANY, u"Place", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText24.Wrap( -1 )

		fgSizer5.Add( self.m_staticText24, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		choicePlaceChoices = []
		self.choicePlace = wx.Choice( sizerSettings.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choicePlaceChoices, 0 )
		self.choicePlace.SetSelection( 0 )
		fgSizer5.Add( self.choicePlace, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_staticText29 = wx.StaticText( sizerSettings.GetStaticBox(), wx.ID_ANY, u"Group", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText29.Wrap( -1 )

		fgSizer5.Add( self.m_staticText29, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		choiceGroupChoices = []
		self.choiceGroup = wx.Choice( sizerSettings.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choiceGroupChoices, 0 )
		self.choiceGroup.SetSelection( 0 )
		fgSizer5.Add( self.choiceGroup, 0, wx.ALL|wx.EXPAND, 5 )


		bSizer57.Add( fgSizer5, 1, wx.ALIGN_CENTER, 5 )

		sbSizer7 = wx.StaticBoxSizer( wx.StaticBox( sizerSettings.GetStaticBox(), wx.ID_ANY, u"Solver" ), wx.HORIZONTAL )

		self.useAltCharacter = wx.CheckBox( sbSizer7.GetStaticBox(), wx.ID_ANY, u"Use alt character", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer7.Add( self.useAltCharacter, 1, wx.ALL, 5 )

		self.useAltVoice = wx.CheckBox( sbSizer7.GetStaticBox(), wx.ID_ANY, u"Use alt character voice", wx.DefaultPosition, wx.DefaultSize, 0 )
		sbSizer7.Add( self.useAltVoice, 1, wx.ALL, 5 )


		bSizer57.Add( sbSizer7, 0, wx.EXPAND, 5 )


		sizerSettings.Add( bSizer57, 1, wx.EXPAND, 5 )


		sizerParams.Add( sizerSettings, 4, wx.ALL|wx.EXPAND, 5 )


		bSizer22.Add( sizerParams, 1, wx.EXPAND, 5 )


		self.paneEditParam.GetPane().SetSizer( bSizer22 )
		self.paneEditParam.GetPane().Layout()
		bSizer22.Fit( self.paneEditParam.GetPane() )
		editorMainSizer.Add( self.paneEditParam, 0, wx.EXPAND |wx.ALL, 5 )

		self.m_staticline6 = wx.StaticLine( self.editorScroll, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		editorMainSizer.Add( self.m_staticline6, 0, wx.EXPAND, 5 )

		self.paneEditText = wx.CollapsiblePane( self.editorScroll, wx.ID_ANY, u"Text", wx.DefaultPosition, wx.DefaultSize, wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE )
		self.paneEditText.Collapse( False )

		bSizer23 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer23.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_panel9 = wx.Panel( self.paneEditText.GetPane(), wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.TAB_TRAVERSAL )
		self.m_panel9.SetMinSize( wx.Size( 440,-1 ) )
		self.m_panel9.SetMaxSize( wx.Size( 540,-1 ) )

		bSizer52 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer26 = wx.BoxSizer( wx.VERTICAL )

		bSizer25 = wx.BoxSizer( wx.HORIZONTAL )

		self.m_staticText19 = wx.StaticText( self.m_panel9, wx.ID_ANY, u"Preview", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText19.Wrap( -1 )

		bSizer25.Add( self.m_staticText19, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

		textSelectChoiceChoices = [ u"Hint 1", u"Hint 2", u"Hint 3", u"Prompt", u"On Failed", u"On Solved" ]
		self.textSelectChoice = wx.Choice( self.m_panel9, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, textSelectChoiceChoices, 0 )
		self.textSelectChoice.SetSelection( 5 )
		bSizer25.Add( self.textSelectChoice, 1, wx.ALL, 5 )


		bSizer26.Add( bSizer25, 0, wx.EXPAND, 5 )

		self.textEdit = wx.TextCtrl( self.m_panel9, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_DONTWRAP|wx.TE_MULTILINE )
		bSizer26.Add( self.textEdit, 1, wx.BOTTOM|wx.EXPAND|wx.LEFT|wx.RIGHT, 5 )


		bSizer52.Add( bSizer26, 1, wx.EXPAND, 5 )

		self.hintPreview = wx.StaticBitmap( self.m_panel9, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 256,192 ), 0 )
		self.hintPreview.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INFOBK ) )
		self.hintPreview.SetMinSize( wx.Size( 256,192 ) )
		self.hintPreview.SetMaxSize( wx.Size( 256,192 ) )

		bSizer52.Add( self.hintPreview, 0, wx.ALL, 5 )


		self.m_panel9.SetSizer( bSizer52 )
		self.m_panel9.Layout()
		bSizer52.Fit( self.m_panel9 )
		bSizer23.Add( self.m_panel9, 100, wx.EXPAND, 5 )


		bSizer23.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		self.paneEditText.GetPane().SetSizer( bSizer23 )
		self.paneEditText.GetPane().Layout()
		bSizer23.Fit( self.paneEditText.GetPane() )
		editorMainSizer.Add( self.paneEditText, 0, wx.EXPAND |wx.ALL, 5 )

		self.m_staticline7 = wx.StaticLine( self.editorScroll, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		editorMainSizer.Add( self.m_staticline7, 0, wx.EXPAND, 5 )

		self.paneEditBackgrounds = wx.CollapsiblePane( self.editorScroll, wx.ID_ANY, u"Backgrounds", wx.DefaultPosition, wx.DefaultSize, wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE )
		self.paneEditBackgrounds.Collapse( True )

		wSizer3 = wx.WrapSizer( wx.HORIZONTAL, wx.REMOVE_LEADING_SPACES )

		sbSizer2 = wx.StaticBoxSizer( wx.StaticBox( self.paneEditBackgrounds.GetPane(), wx.ID_ANY, u"Top Screen" ), wx.HORIZONTAL )

		self.previewBackgroundSub = wx.StaticBitmap( sbSizer2.GetStaticBox(), wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 256,192 ), 0 )
		self.previewBackgroundSub.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INFOBK ) )

		sbSizer2.Add( self.previewBackgroundSub, 0, wx.ALL, 5 )

		bSizer33 = wx.BoxSizer( wx.VERTICAL )

		self.changeBackgroundSub = wx.Button( sbSizer2.GetStaticBox(), wx.ID_ANY, u"Change", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer33.Add( self.changeBackgroundSub, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_staticText27 = wx.StaticText( sbSizer2.GetStaticBox(), wx.ID_ANY, u"Images for the top screen are presets and not unique to each puzzle. These backgrounds need to be modified within the ROM Overview.", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText27.Wrap( 160 )

		self.m_staticText27.Enable( False )

		bSizer33.Add( self.m_staticText27, 1, wx.ALIGN_CENTER|wx.ALL, 5 )


		sbSizer2.Add( bSizer33, 1, wx.EXPAND, 5 )


		wSizer3.Add( sbSizer2, 1, wx.ALL|wx.EXPAND, 5 )

		sbSizer3 = wx.StaticBoxSizer( wx.StaticBox( self.paneEditBackgrounds.GetPane(), wx.ID_ANY, u"Bottom Screen" ), wx.HORIZONTAL )

		self.previewBackgroundMain = wx.StaticBitmap( sbSizer3.GetStaticBox(), wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 256,192 ), 0 )
		self.previewBackgroundMain.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INFOBK ) )

		sbSizer3.Add( self.previewBackgroundMain, 0, wx.ALL, 5 )

		bSizer32 = wx.BoxSizer( wx.VERTICAL )

		self.changeBackgroundMain = wx.Button( sbSizer3.GetStaticBox(), wx.ID_ANY, u"Change", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer32.Add( self.changeBackgroundMain, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_checkBox1 = wx.CheckBox( sbSizer3.GetStaticBox(), wx.ID_ANY, u"Force unique image", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox1.Enable( False )
		self.m_checkBox1.SetToolTip( u"Backgrounds can be shared across different puzzles. By default, selecting an image shares the resource with its peers. Check this to create a copy of the resource for this puzzle only." )

		bSizer32.Add( self.m_checkBox1, 0, wx.ALL, 5 )

		self.m_checkBox5 = wx.CheckBox( sbSizer3.GetStaticBox(), wx.ID_ANY, u"Locale-dependent", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox5.Enable( False )
		self.m_checkBox5.SetToolTip( u"Check this if your background includes elements that may need translating depending on the player's locale. This may be greyed out if the image is a shared asset." )

		bSizer32.Add( self.m_checkBox5, 0, wx.ALL, 5 )


		sbSizer3.Add( bSizer32, 1, wx.EXPAND, 5 )


		wSizer3.Add( sbSizer3, 1, wx.ALL|wx.EXPAND, 5 )

		sbSizer31 = wx.StaticBoxSizer( wx.StaticBox( self.paneEditBackgrounds.GetPane(), wx.ID_ANY, u"Answer Screen" ), wx.HORIZONTAL )

		self.previewBackgroundAnswer = wx.StaticBitmap( sbSizer31.GetStaticBox(), wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 256,192 ), 0 )
		self.previewBackgroundAnswer.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INFOBK ) )

		sbSizer31.Add( self.previewBackgroundAnswer, 0, wx.ALL, 5 )

		bSizer321 = wx.BoxSizer( wx.VERTICAL )

		self.changeBackgroundMain1 = wx.Button( sbSizer31.GetStaticBox(), wx.ID_ANY, u"Change", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer321.Add( self.changeBackgroundMain1, 0, wx.ALL|wx.EXPAND, 5 )

		self.changeBackgroundMain11 = wx.Button( sbSizer31.GetStaticBox(), wx.ID_ANY, u"Remove", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.changeBackgroundMain11.Enable( False )
		self.changeBackgroundMain11.SetToolTip( u"Remove the selected background from the answer screen. When the puzzle is solved, the top screen image will be used instead. " )

		bSizer321.Add( self.changeBackgroundMain11, 0, wx.ALL|wx.EXPAND, 5 )

		self.m_checkBox11 = wx.CheckBox( sbSizer31.GetStaticBox(), wx.ID_ANY, u"Force unique image", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox11.Enable( False )
		self.m_checkBox11.SetToolTip( u"Backgrounds can be shared across different puzzles. By default, selecting an image shares the resource with its peers. Check this to create a copy of the resource for this puzzle only." )

		bSizer321.Add( self.m_checkBox11, 0, wx.ALL, 5 )

		self.m_checkBox51 = wx.CheckBox( sbSizer31.GetStaticBox(), wx.ID_ANY, u"Locale-dependent", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_checkBox51.Enable( False )
		self.m_checkBox51.SetToolTip( u"Check this if your background includes elements that may need translating depending on the player's locale. This may be greyed out if the image is a shared asset." )

		bSizer321.Add( self.m_checkBox51, 0, wx.ALL, 5 )


		sbSizer31.Add( bSizer321, 1, wx.EXPAND, 5 )


		wSizer3.Add( sbSizer31, 1, wx.ALL|wx.EXPAND, 5 )


		self.paneEditBackgrounds.GetPane().SetSizer( wSizer3 )
		self.paneEditBackgrounds.GetPane().Layout()
		wSizer3.Fit( self.paneEditBackgrounds.GetPane() )
		editorMainSizer.Add( self.paneEditBackgrounds, 0, wx.EXPAND |wx.ALL, 5 )

		self.m_staticline71 = wx.StaticLine( self.editorScroll, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		editorMainSizer.Add( self.m_staticline71, 0, wx.EXPAND, 5 )

		self.paneGameplayEditor = wx.CollapsiblePane( self.editorScroll, wx.ID_ANY, u"Gameplay", wx.DefaultPosition, wx.DefaultSize, wx.CP_DEFAULT_STYLE|wx.CP_NO_TLW_RESIZE )
		self.paneGameplayEditor.Collapse( False )

		bSizer49 = wx.BoxSizer( wx.HORIZONTAL )

		bSizer84 = wx.BoxSizer( wx.VERTICAL )

		sbSizer34 = wx.StaticBoxSizer( wx.StaticBox( self.paneGameplayEditor.GetPane(), wx.ID_ANY, u"Page" ), wx.VERTICAL )

		bSizer83 = wx.BoxSizer( wx.HORIZONTAL )

		m_choice33Choices = []
		self.m_choice33 = wx.Choice( sbSizer34.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice33Choices, 0 )
		self.m_choice33.SetSelection( 0 )
		bSizer83.Add( self.m_choice33, 2, wx.ALL|wx.EXPAND, 5 )

		self.m_button62 = wx.Button( sbSizer34.GetStaticBox(), wx.ID_ANY, u"Add", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer83.Add( self.m_button62, 0, wx.ALL, 5 )

		self.m_button63 = wx.Button( sbSizer34.GetStaticBox(), wx.ID_ANY, u"Delete", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer83.Add( self.m_button63, 0, wx.ALL, 5 )


		sbSizer34.Add( bSizer83, 0, wx.EXPAND, 5 )


		bSizer84.Add( sbSizer34, 0, wx.EXPAND, 5 )

		sbSizer35 = wx.StaticBoxSizer( wx.StaticBox( self.paneGameplayEditor.GetPane(), wx.ID_ANY, u"Interaction Zones" ), wx.VERTICAL )

		self.listZones = wx.ListCtrl( sbSizer35.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LC_AUTOARRANGE|wx.LC_ICON )
		sbSizer35.Add( self.listZones, 1, wx.ALL|wx.EXPAND, 5 )

		self.propGridDraw = pg.PropertyGrid(sbSizer35.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.propgrid.PG_DEFAULT_STYLE|wx.propgrid.PG_HIDE_MARGIN)
		self.m_propertyGridItem1 = self.propGridDraw.Append( pg.FloatProperty( u"Radius", u"Radius" ) )
		self.m_propertyGridItem2 = self.propGridDraw.Append( pg.IntProperty( u"Position (X)", u"Position (X)" ) )
		self.m_propertyGridItem21 = self.propGridDraw.Append( pg.IntProperty( u"Position (Y)", u"Position (Y)" ) )
		self.m_propertyGridItem6 = self.propGridDraw.Append( pg.BoolProperty( u"Solution?", u"Solution?" ) )
		sbSizer35.Add( self.propGridDraw, 1, wx.ALL|wx.EXPAND, 5 )

		bSizer85 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer85.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.m_button64 = wx.Button( sbSizer35.GetStaticBox(), wx.ID_ANY, u"Add", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer85.Add( self.m_button64, 0, wx.ALL, 5 )

		self.m_button65 = wx.Button( sbSizer35.GetStaticBox(), wx.ID_ANY, u"Delete", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer85.Add( self.m_button65, 0, wx.ALL, 5 )


		sbSizer35.Add( bSizer85, 0, wx.EXPAND, 5 )


		bSizer84.Add( sbSizer35, 1, wx.EXPAND, 5 )


		bSizer49.Add( bSizer84, 1, wx.EXPAND, 5 )

		sbSizer21 = wx.StaticBoxSizer( wx.StaticBox( self.paneGameplayEditor.GetPane(), wx.ID_ANY, u"Page Preview" ), wx.VERTICAL )

		self.bgInput = wx.StaticBitmap( sbSizer21.GetStaticBox(), wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 256,192 ), 0 )
		self.bgInput.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INFOBK ) )

		sbSizer21.Add( self.bgInput, 0, wx.ALL, 5 )


		bSizer49.Add( sbSizer21, 0, wx.ALIGN_CENTER|wx.ALL, 5 )


		self.paneGameplayEditor.GetPane().SetSizer( bSizer49 )
		self.paneGameplayEditor.GetPane().Layout()
		bSizer49.Fit( self.paneGameplayEditor.GetPane() )
		editorMainSizer.Add( self.paneGameplayEditor, 0, wx.EXPAND |wx.ALL, 5 )


		self.editorScroll.SetSizer( editorMainSizer )
		self.editorScroll.Layout()
		editorMainSizer.Fit( self.editorScroll )
		bSizer20.Add( self.editorScroll, 1, wx.EXPAND |wx.ALL, 5 )


		self.SetSizer( bSizer20 )
		self.Layout()

		# Connect Events
		self.Bind( wx.aui.EVT_AUI_PANE_ACTIVATED, self.editorPuzzleOnAuiPaneActivated )
		self.editorScroll.Bind( wx.EVT_SIZE, self.editorScrollOnSize )
		self.paneEditParam.Bind( wx.EVT_COLLAPSIBLEPANE_CHANGED, self.paneEditParamOnCollapsiblePaneChanged )
		self.puzzleName.Bind( wx.EVT_TEXT, self.puzzleNameOnText )
		self.puzzlePickExternalId.Bind( wx.EVT_CHOICE, self.puzzlePickExternalIdOnChoice )
		self.puzzlePickTutorialId.Bind( wx.EVT_CHOICE, self.puzzlePickTutorialIdOnChoice )
		self.puzzlePicaratMax.Bind( wx.EVT_TEXT, self.puzzlePicaratMaxOnText )
		self.puzzlePicaratMid.Bind( wx.EVT_TEXT, self.puzzlePicaratMidOnText )
		self.puzzlePicaratMin.Bind( wx.EVT_TEXT, self.puzzlePicaratMinOnText )
		self.choiceReward.Bind( wx.EVT_CHOICE, self.choiceRewardOnChoice )
		self.choicePlace.Bind( wx.EVT_CHOICE, self.choicePlaceOnChoice )
		self.choiceGroup.Bind( wx.EVT_CHOICE, self.choiceGroupOnChoice )
		self.useAltCharacter.Bind( wx.EVT_CHECKBOX, self.useAltCharacterOnCheckBox )
		self.useAltVoice.Bind( wx.EVT_CHECKBOX, self.useAltVoiceOnCheckBox )
		self.paneEditText.Bind( wx.EVT_COLLAPSIBLEPANE_CHANGED, self.paneEditTextOnCollapsiblePaneChanged )
		self.textSelectChoice.Bind( wx.EVT_CHOICE, self.textSelectChoiceOnChoice )
		self.textEdit.Bind( wx.EVT_TEXT, self.textEditOnText )
		self.paneEditBackgrounds.Bind( wx.EVT_COLLAPSIBLEPANE_CHANGED, self.paneEditBackgroundsOnCollapsiblePaneChanged )
		self.paneGameplayEditor.Bind( wx.EVT_COLLAPSIBLEPANE_CHANGED, self.paneGameplayEditorOnCollapsiblePaneChanged )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def editorPuzzleOnAuiPaneActivated( self, event ):
		event.Skip()

	def editorScrollOnSize( self, event ):
		event.Skip()

	def paneEditParamOnCollapsiblePaneChanged( self, event ):
		event.Skip()

	def puzzleNameOnText( self, event ):
		event.Skip()

	def puzzlePickExternalIdOnChoice( self, event ):
		event.Skip()

	def puzzlePickTutorialIdOnChoice( self, event ):
		event.Skip()

	def puzzlePicaratMaxOnText( self, event ):
		event.Skip()

	def puzzlePicaratMidOnText( self, event ):
		event.Skip()

	def puzzlePicaratMinOnText( self, event ):
		event.Skip()

	def choiceRewardOnChoice( self, event ):
		event.Skip()

	def choicePlaceOnChoice( self, event ):
		event.Skip()

	def choiceGroupOnChoice( self, event ):
		event.Skip()

	def useAltCharacterOnCheckBox( self, event ):
		event.Skip()

	def useAltVoiceOnCheckBox( self, event ):
		event.Skip()

	def paneEditTextOnCollapsiblePaneChanged( self, event ):
		event.Skip()

	def textSelectChoiceOnChoice( self, event ):
		event.Skip()

	def textEditOnText( self, event ):
		event.Skip()

	def paneEditBackgroundsOnCollapsiblePaneChanged( self, event ):
		event.Skip()

	def paneGameplayEditorOnCollapsiblePaneChanged( self, event ):
		event.Skip()


###########################################################################
## Class editorDrawInput
###########################################################################

class editorDrawInput ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 600,278 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		self.SetMinSize( wx.Size( 600,278 ) )

		bSizer49 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer49.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		sbSizer16 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Answer" ), wx.VERTICAL )

		fgSizer31 = wx.FlexGridSizer( 4, 2, 0, 0 )
		fgSizer31.SetFlexibleDirection( wx.HORIZONTAL )
		fgSizer31.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

		self.m_staticText252 = wx.StaticText( sbSizer16.GetStaticBox(), wx.ID_ANY, u"Type", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText252.Wrap( -1 )

		fgSizer31.Add( self.m_staticText252, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		drawInputPickTypeChoices = [ u"Alphabetical, 1-4 characters", u"Numerical, 1-4 digits", u"Numerical, 1:1 digit ratio", u"Numerical, 3 digits", u"Numerical, 2:2 digit ratio" ]
		self.drawInputPickType = wx.Choice( sbSizer16.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), drawInputPickTypeChoices, 0 )
		self.drawInputPickType.SetSelection( 0 )
		self.drawInputPickType.SetToolTip( u"Sets the type of this puzzle. Where possible, use the least general type that suits your answer. Ranges mean that type can be adapted to fit any amount of digits in that range." )

		fgSizer31.Add( self.drawInputPickType, 1, wx.ALL|wx.EXPAND, 5 )

		self.m_staticText251 = wx.StaticText( sbSizer16.GetStaticBox(), wx.ID_ANY, u"Input Length", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText251.Wrap( -1 )

		fgSizer31.Add( self.m_staticText251, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		drawInputSetLengthChoices = [ u"1", u"2", u"3", u"4" ]
		self.drawInputSetLength = wx.Choice( sbSizer16.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), drawInputSetLengthChoices, 0 )
		self.drawInputSetLength.SetSelection( 0 )
		self.drawInputSetLength.SetToolTip( u"Controls how long the input box should be. The answer must fit in the same amount of space." )

		fgSizer31.Add( self.drawInputSetLength, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_staticText261 = wx.StaticText( sbSizer16.GetStaticBox(), wx.ID_ANY, u"Answer", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText261.Wrap( -1 )

		fgSizer31.Add( self.m_staticText261, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.drawInputSetAnswer = wx.TextCtrl( sbSizer16.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTER )
		fgSizer31.Add( self.drawInputSetAnswer, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.m_staticText2521 = wx.StaticText( sbSizer16.GetStaticBox(), wx.ID_ANY, u"Debug", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText2521.Wrap( -1 )

		self.m_staticText2521.Enable( False )

		fgSizer31.Add( self.m_staticText2521, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		drawInputPickDebugChoices = [ u"Subtype 0", u"Subtype 1", u"Subtype 2" ]
		self.drawInputPickDebug = wx.Choice( sbSizer16.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), drawInputPickDebugChoices, 0 )
		self.drawInputPickDebug.SetSelection( 0 )
		fgSizer31.Add( self.drawInputPickDebug, 0, wx.ALL|wx.EXPAND, 5 )


		sbSizer16.Add( fgSizer31, 1, wx.EXPAND, 5 )

		self.m_staticText40 = wx.StaticText( sbSizer16.GetStaticBox(), wx.ID_ANY, u"Some fields may be grayed out due to your\nselected options. Debug options are for\ntesting and can be ignored.", wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTER_HORIZONTAL )
		self.m_staticText40.Wrap( -1 )

		self.m_staticText40.Enable( False )

		sbSizer16.Add( self.m_staticText40, 0, wx.ALIGN_CENTER|wx.ALL, 5 )


		bSizer49.Add( sbSizer16, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		sbSizer21 = wx.StaticBoxSizer( wx.StaticBox( self, wx.ID_ANY, u"Input Screen" ), wx.VERTICAL )

		self.bgInput = wx.StaticBitmap( sbSizer21.GetStaticBox(), wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.Size( 256,192 ), 0 )
		self.bgInput.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INFOBK ) )

		sbSizer21.Add( self.bgInput, 0, wx.ALL, 5 )

		bSizer331 = wx.BoxSizer( wx.HORIZONTAL )


		bSizer331.Add( ( 0, 0), 1, wx.EXPAND, 5 )

		self.changeBackgroundSub1 = wx.Button( sbSizer21.GetStaticBox(), wx.ID_ANY, u"Change", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer331.Add( self.changeBackgroundSub1, 0, wx.ALIGN_CENTER|wx.ALL, 5 )

		self.buttonGenerateTemplate = wx.Button( sbSizer21.GetStaticBox(), wx.ID_ANY, u"   Generate Template   ", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.buttonGenerateTemplate.SetToolTip( u"Creates an image with outlines for where elements need to be drawn." )

		bSizer331.Add( self.buttonGenerateTemplate, 0, wx.ALIGN_CENTER|wx.ALL, 5 )


		bSizer331.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		sbSizer21.Add( bSizer331, 0, wx.EXPAND, 5 )


		bSizer49.Add( sbSizer21, 0, wx.ALIGN_CENTER|wx.ALL, 5 )


		bSizer49.Add( ( 0, 0), 1, wx.EXPAND, 5 )


		self.SetSizer( bSizer49 )
		self.Layout()

		# Connect Events
		self.drawInputPickType.Bind( wx.EVT_CHOICE, self.drawInputPickTypeOnChoice )
		self.drawInputSetLength.Bind( wx.EVT_CHOICE, self.drawInputSetLengthOnChoice )
		self.drawInputSetAnswer.Bind( wx.EVT_TEXT, self.drawInputSetAnswerOnText )
		self.drawInputPickDebug.Bind( wx.EVT_CHOICE, self.drawInputPickDebugOnChoice )

	def __del__( self ):
		pass


	# Virtual event handlers, override them in your derived class
	def drawInputPickTypeOnChoice( self, event ):
		event.Skip()

	def drawInputSetLengthOnChoice( self, event ):
		event.Skip()

	def drawInputSetAnswerOnText( self, event ):
		event.Skip()

	def drawInputPickDebugOnChoice( self, event ):
		event.Skip()


###########################################################################
## Class editorFreeInput
###########################################################################

class editorFreeInput ( wx.Panel ):

	def __init__( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 600,278 ), style = wx.TAB_TRAVERSAL, name = wx.EmptyString ):
		wx.Panel.__init__ ( self, parent, id = id, pos = pos, size = size, style = style, name = name )

		self.SetMinSize( wx.Size( 600,278 ) )


	def __del__( self ):
		pass


