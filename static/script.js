document.addEventListener("DOMContentLoaded",()=>{

const cards = document.querySelectorAll(".card")

cards.forEach((card,i)=>{

card.style.opacity="0"
card.style.transform="translateY(20px)"

setTimeout(()=>{

card.style.opacity="1"
card.style.transform="translateY(0)"
card.style.transition="0.6s"

},i*200)

})

})