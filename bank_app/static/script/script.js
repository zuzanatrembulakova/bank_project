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

// When making a POST request to Django, we need to include the csrf token 
// to prevent Cross Site Request Forgery attacks. The Django docs give the exact 
// JavaScript code we need to add to get the token from the csrftoken cookie.
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function curenncyChange(){

    if (one("#from_currency").value != "" && one("#to_currency").value != ""){
        let c1 = one("#from_currency").value
        let c2 = one("#to_currency").value

        if (c1 != c2){
            fetch("api/currency_ratio/" + c1 + "/" + c2, {
                method: 'GET',
                credentials: 'same-origin',
                headers:{
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest', 
                    'X-CSRFToken': getCookie('csrftoken'),
                },
            })
            .then(response => {
                if (response.status == 200){
    
                    response.json().then(data => ({
                        data: data,
                    })).then(res => {
                        one("#rate").value = res.data.res
                    })
    
                } else {
                    return null;
                }
            })
        } else {
            alert("Choose two different currencies")
        }        
    }     
}


function updateRate(){
    let c1 = one("#from_currency").value
    let c2 = one("#to_currency").value

    let new_rate = one("#rate").value

    let obj = new Object()
    obj.ratio = new_rate

    if (new_rate != ''){
        fetch("api/currency_ratio/" + c1 + "/" + c2, {
            method: "PUT",
            credentials: 'same-origin',
            headers:{
    
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest', 
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify(obj)
        })
    }
}
