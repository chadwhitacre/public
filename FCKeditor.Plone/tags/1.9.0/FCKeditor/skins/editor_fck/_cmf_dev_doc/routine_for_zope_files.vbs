Rem Exemple de fonction servant à mettre des fichiers en cache pour produits plone
Rem Faut juste changer le fisikpath
Dim FSO
Set FSO = CreateObject ("Scripting.FileSystemObject")
Fisikpath = "F:\WebDev\Zope\FCKEDITOR DEV\plone product 2.0 fc preview\FCKeditor\skins\editor_fck\editor\plugins\tablecommands\"
Set folder = FSO.GetFolder(Fisikpath)

For each item in folder.files

 newFileName = item.name & ".metadata"

 If FSO.FileExists(Fisikpath & "\" & newFileName)= false and Instr(item.name,".metadata")=0 Then

  FSO.CreateTextFile(Fisikpath & "\" & newFileName)
  Set file = FSO.OpenTextFile (Fisikpath & "\" & newFileName,2,true,0)
  
  file.write "[default]" & chr(13) & chr(10) & "cache = HTTPCache" & chr(13) & chr(10)

  Set file = Nothing

 End If

Next

Set folder = Nothing
Set FSO = Nothing