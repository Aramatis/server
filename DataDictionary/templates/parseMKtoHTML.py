"""
to update succesfuly this feature run the following comnads from the root of the project

python manage.py listing_models --format md > DataDictionary/templates/dataDic.md
cd DataDictionary/templates/
python parseMKtoHTML.py
"""

destHTML = open("dataDic.html","w")
readMK   = open("dataDic.md","r") 

destHTML.write('''
<!DOCTYPE html>
<html>
	<title>TransApp model Dictionary</title>

	<xmp theme="united" style="display:none;">''')

for line in readMK:
	destHTML.write(line)

destHTML.write('''
	</xmp>
	<script src="http://strapdownjs.com/v/0.2/strapdown.js"></script>
</html>''')

destHTML.close()
readMK.close()