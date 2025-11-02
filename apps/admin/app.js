// Mobile menu
function toggleMenu(){
  const nav = document.querySelector('nav');
  nav.style.display = (nav.style.display === 'flex') ? 'none' : 'flex';
}

// Basket logic
const basket = [];
const basketList = document.getElementById('basketList');
const basketTotal = document.getElementById('basketTotal');

function formatCHF(n){ return 'CHF ' + Number(n).toFixed(0); }

function renderBasket(){
  basketList.innerHTML = '';
  let total = 0;
  basket.forEach((item, idx)=>{
    total += item.price;
    const li = document.createElement('li');
    li.innerHTML = `<span>${item.name}</span><span class="badge">${formatCHF(item.price)}</span>
      <button class="rm" onclick="removeItem(${idx})">Entfernen</button>`;
    basketList.appendChild(li);
  });
  basketTotal.textContent = formatCHF(total);
}

function removeItem(index){
  basket.splice(index,1);
  renderBasket();
}

function clearBasket(){
  basket.length = 0;
  renderBasket();
}

document.querySelectorAll('.add').forEach(btn=>{
  btn.addEventListener('click', ()=>{
    const name = btn.dataset.name;
    const price = Number(btn.dataset.price||0);
    basket.push({name, price});
    renderBasket();
    document.getElementById('booking').scrollIntoView({behavior:'smooth'});
  });
});

// Booking
function buildMessage(){
  const name = document.getElementById('name').value.trim();
  const phone = document.getElementById('phone').value.trim();
  const email = document.getElementById('email').value.trim();
  const date = document.getElementById('date').value;
  const notes = document.getElementById('notes').value.trim();

  const lines = [];
  lines.push('Neue Terminanfrage – Coiffeur Shatha');
  lines.push('—');
  lines.push('Name: ' + name);
  lines.push('Telefon: ' + phone);
  if(email) lines.push('E-Mail: ' + email);
  if(date)  lines.push('Wunschtermin: ' + new Date(date).toLocaleString('de-CH'));
  lines.push('— Gewählte Leistungen —');
  if(basket.length===0){ lines.push('(keine Auswahl – bitte beraten)'); }
  else{
    basket.forEach(i=> lines.push(`• ${i.name} – CHF ${i.price}`));
    const sum = basket.reduce((a,b)=>a+b.price,0);
    lines.push('Zwischensumme: CHF ' + sum);
  }
  if(notes){ lines.push('— Notizen —'); lines.push(notes); }
  lines.push('Vielen Dank!');
  return lines.join('\n');
}

function sendRequest(e){
  e.preventDefault();
  const msg = buildMessage();
  const phoneE164 = '41788057078'; // WhatsApp Zielnummer (ohne +)
  const url = 'https://wa.me/' + phoneE164 + '?text=' + encodeURIComponent(msg);
  window.open(url, '_blank');
  return false;
}

function sendEmail(){
  const msg = buildMessage();
  const subject = encodeURIComponent('Terminanfrage – Coiffeur Shatha');
  const body = encodeURIComponent(msg);
  window.location.href = 'mailto:info@shatha.ch?subject=' + subject + '&body=' + body;
}

// Year
document.getElementById('year').textContent = new Date().getFullYear();
