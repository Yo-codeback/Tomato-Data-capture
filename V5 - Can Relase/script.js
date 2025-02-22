// 時鐘與日期更新
function updateTime() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    document.getElementById('clock').textContent = `${hours}:${minutes}:${seconds}`;

    // 民國日期轉換
    const year = now.getFullYear() - 1911;
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    document.getElementById('date').textContent = `${year}/${month}/${day}`;

    // 星期轉換
    const weekdays = ['日', '一', '二', '三', '四', '五', '六'];
    document.getElementById('weekday').textContent = `星期${weekdays[now.getDay()]}`;
}

setInterval(updateTime, 1000);
updateTime();

// 2~3 組跑馬燈輪流單字滾動
const marqueeTexts = ["系統測試請管理人員設定", "數據更新中請稍後", "交易數據即將顯示"];
let marqueeIndex = 0;
let charIndex = 0;

function updateMarquee() {
    let text = marqueeTexts[marqueeIndex];
    let char = text[charIndex];
    
    for (let i = 1; i <= 3; i++) {
        document.getElementById(`marquee${i}`).textContent = char;
    }

    for (let i = 1; i <= 3; i++) {
        document.getElementById(`marquee${i}`).style.animation = "none";
    }

    setTimeout(() => {
        for (let i = 1; i <= 3; i++) {
            document.getElementById(`marquee${i}`).style.animation = "scrollUp 0.3s ease-in-out";
        }
    }, 50);

    charIndex++;
    if (charIndex >= text.length) {
        charIndex = 0;
        marqueeIndex = (marqueeIndex + 1) % marqueeTexts.length;
    }
}

setInterval(updateMarquee, 1000);
updateMarquee();

// 抓取 JSON 資料
async function fetchData() {
    try {
        const response = await fetch('taipei_data.json');
        if (!response.ok) throw new Error('資料抓取失敗');

        const data = await response.json();
        const today = new Date();
        const todayStr = `${today.getFullYear() - 1911}.${String(today.getMonth() + 1).padStart(2, '0')}.${String(today.getDate()).padStart(2, '0')}`;

        const todayData = data.find(item => item["交易日期"] === todayStr);
        if (todayData) {
            document.getElementById('today-date').textContent = todayData["交易日期"];
            document.getElementById('market-name').textContent = todayData["市場名稱"];
            document.getElementById('average-price').textContent = todayData["平均價"];
            document.getElementById('trade-volume').textContent = todayData["交易量"];
        } else {
            throw new Error('今日資料未找到');
        }
    } catch (error) {
        console.error(error);
    }
}

fetchData();
setInterval(fetchData, 180000);
