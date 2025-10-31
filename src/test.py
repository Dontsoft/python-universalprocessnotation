import universalprocessnotation
import universalprocessnotation.process

process = universalprocessnotation.process.Process("Salesforce Example")

progress_lead = process.add_block("Progress lead", ["Incoming lead"])
progress_lead.connect_end("Incomplete data")
progress_lead.add_who("Account", responsible=True, accountable=True)
progress_lead.add_system("Sales Cloud")


run_campaign = progress_lead.connect_new("Lead", "Run campaign")
run_campaign.connect_end("Outreach")
run_campaign.connect("Unsubscribe / privacy", progress_lead)
run_campaign.add_who("Marketing", accountable=True)
run_campaign.add_system("Marketing Cloud")

sell_to_customer = progress_lead.connect_new("Account & Contact", "Sell to customer")
sell_to_customer.add_who("Account Exec", responsible=True)
sell_to_customer.add_system("Sales Cloud")
sell_to_customer.connect("No opportunity", progress_lead)

forecast_revenue = sell_to_customer.connect_new("Opportunities by date", "Forecast revenue")
forecast_revenue.add_who("VP Sales", responsible=True)
forecast_revenue.add_system("Sales Cloud")
forecast_revenue.connect_end("Forecast")

raise_and_accept_quote = sell_to_customer.connect_new(
    "Closed opportunity & product", "Raise and accept quote", ["Price book"])
raise_and_accept_quote.add_who("Finance administrator", responsible=True)
raise_and_accept_quote.add_who("Customer", informed=True)
raise_and_accept_quote.add_system("Revenue Cloud")

raise_and_confirm_order = raise_and_accept_quote.connect_new("Accepted", "Raise and confirm order")
raise_and_confirm_order.add_who("Customer", accountable=True)
raise_and_confirm_order.add_system("Revenue Cloud")

ship_product = raise_and_confirm_order.connect_new("Confirmed", "Ship product with more words wtf I need more lines")
ship_product.add_who("Manufacturing", responsible=True)
ship_product.add_system("ERP")
ship_product.add_system("More")
ship_product.add_system("More")

raise_invoice = raise_and_confirm_order.connect_new("Confirmed", "Raise invoice")
raise_invoice.add_who("Finance administrator", responsible=True)
raise_invoice.add_system("Revenue Cloud")

raise_payment = ship_product.connect_new("Received", "Raise payment")
raise_payment.add_who("Customer", responsible=True, accountable=True)
raise_payment.add_who("Finance administrator",
                      responsible=True)
raise_invoice.connect("Invoice", raise_payment)

book_revenue = raise_invoice.connect_new("Invoice", "Book revenue")
book_revenue.add_who("Finance administrator", responsible=True)
book_revenue.add_system("Revenue Cloud")
book_revenue.connect_end("Revenue")
book_revenue.connect_end("Commission")

ship_product.connect("Received", book_revenue)
raise_payment.connect("Payment & non-payment", book_revenue)


process.to_svg("")

# import svg

# width = ship_product.calculate_width()
# height = ship_product.calculate_height()
# print(svg.SVG(style="text {font-family: sans-serif;}", width=width + 200, height=height + 8, elements=[svg.G(transform="translate(2.0, 2.0)", elements=[ship_product.to_svg(width, height)])]))
