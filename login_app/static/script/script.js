function one(q){
    return document.querySelector(q)
}
function all(q){
    return document.querySelectorAll(q)
}

function openModal(id){
    console.log(id)
    one('#modal_' + id).style.display = 'block'
}
function closeModal(id){
    one('#modal_' + id).style.display = 'none'
}

function showAutomaticPayment() {
    let checkBox = one("#aut_payment_check");
    let details = one("#automatic_payment_details");
    if (checkBox.checked == true){
      details.style.display = "block";
    } else {
       details.style.display = "none";
    }
  }