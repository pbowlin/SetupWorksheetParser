import PyPDF2

# creating a pdf file object 
pdfFileObj = open('TestPDF.pdf','rb')
output_file = open('new_pdf.pdf','wb')

# creating a pdf reader object 
pdfReader = PyPDF2.PdfFileReader(pdfFileObj) 
pdfWriter = PyPDF2.PdfFileWriter()
  
# printing number of pages in pdf file 
print(f'num pages: {pdfReader.numPages}')
  
# creating a page object 
pageObj = pdfReader.getPage(1) 
pdfWriter.addPage(pageObj)

pageObj = pdfReader.getPage(0) 
pdfWriter.addPage(pageObj)

pdfWriter.write(output_file)  

  
# closing the pdf file object 
pdfFileObj.close() 
output_file.close()

