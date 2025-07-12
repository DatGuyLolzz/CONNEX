from flask import Blueprint, render_template, request, redirect, url_for
from .models import db, Ticket, TicketMessage

routes = Blueprint("routes", __name__, template_folder="templates")

@routes.route("/")
def login():
    return render_template("login.html")

@routes.route("/signup")
def signup():
    return render_template("signup.html")

@routes.route('/support')
def support():
    open_tickets = Ticket.query.filter_by(status='open').all()
    closed_tickets = Ticket.query.filter_by(status='closed').all()
    return render_template('support.html', open_tickets=open_tickets, closed_tickets=closed_tickets)

@routes.route('/submit-ticket', methods=['POST'])
def submit_ticket():
    subject = request.form.get('subject')
    message = request.form.get('message')
    # For demo, use static user info; replace with session user in real app
    created_by = "Zamirul"
    user_type = "Elderly"
    ticket = Ticket(subject=subject, message=message, created_by=created_by, user_type=user_type)
    db.session.add(ticket)
    db.session.commit()
    # Add initial message to chat
    ticket_msg = TicketMessage(ticket_id=ticket.id, sender=created_by, content=message)
    db.session.add(ticket_msg)
    db.session.commit()
    return redirect(url_for('routes.support'))

@routes.route('/view-ticket/<int:ticket_id>', methods=['GET', 'POST'])
def view_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    messages = TicketMessage.query.filter_by(ticket_id=ticket_id).order_by(TicketMessage.timestamp).all()
    # Simulate current user info (replace with session in real app)
    current_user = "Zamirul"
    is_admin = False  # Set to True if the current user is admin

    # Allow reply for both admin and ticket owner
    can_reply = is_admin or (current_user == ticket.created_by)

    if request.method == 'POST':
        if not can_reply:
            return redirect(url_for('routes.view_ticket', ticket_id=ticket_id))
        sender = "Admin" if is_admin else current_user
        content = request.form.get('message')
        msg = TicketMessage(ticket_id=ticket_id, sender=sender, content=content)
        db.session.add(msg)
        db.session.commit()
        return redirect(url_for('routes.view_ticket', ticket_id=ticket_id))
    return render_template(
        'view-ticket.html',
        ticket=ticket,
        messages=messages,
        is_admin=is_admin,
        can_reply=can_reply,
        current_user=current_user  # Pass to template
    )

@routes.route('/close-ticket/<int:ticket_id>', methods=['POST'])
def close_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    ticket.status = 'closed'
    db.session.commit()
    return redirect(url_for('routes.view_ticket', ticket_id=ticket_id))

@routes.route('/chats')
def chats():
    return render_template('chats.html')
