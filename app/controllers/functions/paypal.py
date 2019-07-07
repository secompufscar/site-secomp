from app.config.development import PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET
import paypalrestsdk

paypalrestsdk.configure({
  "mode": "sandbox", # sandbox or live
  "client_id": PAYPAL_CLIENT_ID,
  "client_secret": PAYPAL_CLIENT_SECRET })

def criar_pagamento(item, descricao, valor):
    payment = paypalrestsdk.Payment({
    "intent": "sale",
    "payer": {
        "payment_method": "paypal"},
    "redirect_urls": {
        "return_url": "http://localhost:5000/participante/executar-pagamento-kit",
        "cancel_url": "http://localhost:5000/participante/cancelar-pagamento-kit"},
    "transactions": [{
        "item_list": {
            "items": [{
                "name": item,
                "sku": "item",
                "price": valor,
                "currency": "BRL",
                "quantity": 1}]},
        "amount": {
            "total": valor,
            "currency": "BRL"},
        "description": descricao}]})
    if payment.create():
        print("Payment created successfully")
        return payment
    else:
        print(payment.error)
        return None

def encontrar_pagamento(id):
    payment = paypalrestsdk.Payment.find(id)
    return payment
