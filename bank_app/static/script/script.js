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