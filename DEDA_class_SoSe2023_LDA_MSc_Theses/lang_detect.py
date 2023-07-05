import os
from langdetect import detect
import pdfplumber


def de_detect(folder = None, theses = None):
    '''
    Goes through the scraped and downloaded PDF files and scans them to see if they are in German. 
    To save memory, automatically selected to check pages 8, 12, 16, 20, 24; which should in all likelihood cases be body of text.
    '''
    print(f"Current working directory: {os.getcwd()}")

    # List to store German thesis filenames
    german_list = []
    
    for thesis in theses:
        
        with pdfplumber.open(os.path.join(folder, thesis), pages=[8, 12, 16, 20, 24]) as pdf:
            
            print(f'Currently working on {thesis}.')
            
            # Initial condition needed for removing those identified as german
            german = False
            for page in pdf.pages:
                
                text = page.extract_text()
                
                # Try condition necessary as detect() function breaks down on empty pages
                try:
                    if detect(text) == 'de':
                        print(f'{thesis} was identified as German.')
                        german_list.append(thesis)
                        german = True
                        break 
                except:
                    continue
            
            if german:
                pdf.close()
                os.remove(os.path.join(folder,thesis))
                print(f'{thesis} removed from directory')
                    

    print(f'We have identified in total {len(german_list)} German language documents. See below the full list:')
    print(german_list)
    
    return german_list

    