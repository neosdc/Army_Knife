import asyncio
from pyppeteer import launch
from time import sleep

async def close_dialog(dialog):
    print("dialog popup")
    await dialog.dismiss()



async def main():
    browser = await launch()
    page = await browser.newPage()
    await page.goto('http://gw.roigames.co.kr/')
    await page.screenshot({'path': 'example.png'})
    cookies = await page.cookies()
    print(cookies)    
    await page.evaluate('''() => {        
        document.getElementById("gw_user_id").value = "neosdc";
        document.getElementById("gw_user_pw").value = "vrmatrix3";
        encryptSubmit();        
    }''')
	
    sleep(3)
    cookies = await page.cookies()
    print(cookies)

    #대화상자 무시
    page.on('dialog', lambda dialog: asyncio.ensure_future(close_dialog(dialog)))
    await page.goto('http://gw.roigames.co.kr/chtml/groupware/groupware_popup.php?file=gw_indolence_input&mode=attendance_out&employee_id=neosdc')
    sleep(3)
	
    #await page.screenshot({'path': 'example2.png'})
    print(await page.content())

    #print(dimensions)
    # >>> {'width': 800, 'height': 600, 'deviceScaleFactor': 1}
    await browser.close()

asyncio.get_event_loop().run_until_complete(main())

