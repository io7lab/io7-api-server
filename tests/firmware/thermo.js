import { Device, clearCursor, cursorUp }  from './io7device.js';

const min = 15;
const max = 35;
let base_temp = 25.0;
let lowTemp = 22.0;
let highTemp = 28.0;
let columnIndex = {};

function getRandomData(base) {
    return Math.round((base + (Math.random() - 0.5) * 2) * 10) / 10;
}

function adjust(direction, base) {
    if (direction === 'up' && base < max) {
        base = base + 1;
    } else if (direction === 'down' && base > min) {
        base = base - 1;
    }
    setColumnIndex();
    return base;
}

function setColumnIndex() {
    let newIndex = {};
    let step = (max - min) / 10;
    for (let lvl = 10; lvl > 0; lvl--) { columnIndex[lvl] = min + step * lvl }
    return newIndex;
}

function displayThermometer(temp) {
    const tempColor = temp < lowTemp ?  '\x1B[38;5;117m' : temp < highTemp ? '\x1B[38;5;14m' : '\x1B[38;5;196m';
    const resetColor = '\x1B[0m';
    const mercuryLevel = Math.floor(((temp - min) / (max - min)) * 10);

    function colorColumn() {
        for (let lvl = 10; lvl > 0; lvl--) {
            let tempLegend;
            if (lvl === 10) {
                tempLegend = (temp >= columnIndex[lvl]) ? `${temp}°C` : '';
            } else if (lvl === 1) {
                tempLegend = (temp <= columnIndex[lvl]) ? `${temp}°C` : '';
            } else {
                tempLegend = (temp >= columnIndex[lvl] && temp < columnIndex[lvl + 1]) ? `${temp}°C` : '';
            }
            console.log(`           │${mercuryLevel >= lvl ? tempColor + '█' + resetColor : ' '}│  ${tempLegend}`);
        }
    }
    clearCursor();
    
    console.log("Use Up/Down Arrow key to change the base temperature");
    console.log()
    console.log("           ┌─┐");
    colorColumn();
    console.log(`           │${tempColor}█${resetColor}│`);
    console.log(`          ╱${tempColor}███${resetColor}╲`);
    console.log(`         │${tempColor}█████${resetColor}│`);
    console.log(`         │${tempColor}█████${resetColor}│`);
    console.log(`          ╲${tempColor}███${resetColor}╱`);
    console.log("     ");
    console.log(`    Current: ${tempColor}${temp}°C${resetColor}`);
    console.log("     ");
}

export function init(device) {
    let stdin = process.stdin;
    stdin.setRawMode(true);
    stdin.resume();
    stdin.setEncoding('utf8');
    stdin.on('data', function(key){
        if (key === '\u001b[A') {  // Up arrow
            base_temp = adjust('up', base_temp);
        } else if (key === '\u001b[B') {  // Down arrow
            base_temp = adjust('down', base_temp);
        } else if (key === '\u0003' || key === '\u001b') {
            process.exit();
        }
    });
    
    device.loop = () => {
        let temp = getRandomData(base_temp);
        displayThermometer(temp);
        let data = {
            d : {
                temperature : temp
            }
        }
        data.d.humidity = getRandomData(56);
        device.publishEvent('status', JSON.stringify(data));
        console.log(JSON.stringify(data), cursorUp);
    };

    setColumnIndex();
    
    device.connect();
    device.run();
}