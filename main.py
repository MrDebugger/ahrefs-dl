from requests import get
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse
import json,os
def download_file(url,name):
    local_filename = name
    headers = {}
    if os.path.exists(local_filename):
        headers = {'Range': 'bytes=%d-' % (os.path.getsize(local_filename))}
        print("[>] Resuming Video")
    with get(url, stream=True,headers=headers) as r:
        if not r and headers:
            print("[+] Video Already Downloaded")
            return
        total_size = int(r.headers.get('content-length', 0))
        t=tqdm(total=total_size, unit='iB', unit_scale=True)
        r.raise_for_status()
        with open(local_filename, 'ab') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                t.update(len(chunk))
                if chunk: 
                    f.write(chunk)
        t.close()
        if total_size != 0 and t.n != total_size:
            print("ERROR, something went wrong")

COURSE_URL = "https://ahrefs.com/academy/blogging-for-business"
MAIN_SITE = f"{urlparse(COURSE_URL).scheme}://{urlparse(COURSE_URL).netloc}"
r = get(COURSE_URL)
soup = bs(r.text,'lxml')
COURSE_NAME = soup.find(class_='courses-header-container').find('h1').get_text(strip=True)
if not os.path.exists(COURSE_NAME):
    os.mkdir(COURSE_NAME)
chapters = [chapter for chapter in soup.find(class_='contents-lesson__list').findChildren('li',recursive=False)]
chapterId = 1
for chapter in chapters:
	chapterName = chapter.find('h3').get_text(strip=True)
	print(f"[+] Chapter {chapterId}:",chapterName)
	chapterName += f'_{chapterId}'
	if not os.path.exists(COURSE_NAME+'/'+chapterName):
		os.mkdir(COURSE_NAME+'/'+chapterName)
	lessons = [(MAIN_SITE+a['href'],a.find(class_='lessons-excerpt').text) for a in chapter.findAll('a',class_='contents-lesson__list-link')]
	lessonId = 1
	for lesson in lessons:
	    LESSON_URL = lesson[0]
	    LESSON_NAME = lesson[1]
	    print("[>] Downloading:",LESSON_NAME)
	    LESSON_NAME = LESSON_NAME.replace(' ','_').replace('"','').replace('-','_')
	    r = get(LESSON_URL)
	    soup = bs(r.text,'lxml')
	    videoTag = soup.find(class_='wistia_embed').get('class')[1].replace('wistia_async_','')
	    jsonUrl = f"https://fast.wistia.com/embed/medias/{videoTag}.jsonp"
	    print("[>] Getting JSON Data")
	    r = get(jsonUrl)
	    jsonData = json.loads(r.text.split(' = ')[1].split(';')[0])
	    video = jsonData['media']['assets'][0]
	    videoExt = video['ext']
	    videoUrl = video['url']
	    print("[>] Video Found: Downloading")
	    download_file(videoUrl,COURSE_NAME+'/'+chapterName+'/'+LESSON_NAME+f"_{chapterId}_{lessonId}"+'.'+videoExt)
	    print("[+] Downloaded\n")
	    lessonId+=1
	chapterId+=1