from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'nursing_college_secret_key_2024'

# Chat flow data structure
CHAT_STEPS = {
    'welcome': {
        'id': 'welcome',
        'question': 'Namaste! Main aapki Nursing College admission sahayak hun. Kya aap Nursing College mein admission lene mein ruchi rakhte hain?',
        'options': ['Haan', 'Nahi'],
        'next_step': 'eligibility'
    },
    'eligibility': {
        'id': 'eligibility',
        'question': 'Bahut acchi baat hai! Kya aapne 12th class mein Biology padhi hai?',
        'options': ['Haan, Biology padhi hai', 'Nahi, Biology nahi padhi'],
        'next_step': 'program_details'
    },
    'biology_required': {
        'id': 'biology_required',
        'question': 'B.Sc Nursing mein admission ke liye Biology avashyak hai. Kya aap koi aur jaankari chahte hain?',
        'options': ['Haan', 'Nahi'],
        'next_step': 'end'
    },
    'program_details': {
        'id': 'program_details',
        'question': 'Bahut badhiya! Hamara B.Sc Nursing program 4 saal ka full-time course hai. Yeh ek comprehensive program hai jo aapko professional nurse banne ke liye taiyar karta hai. Kya aap is program ke bare mein aur jaankari chahte hain?',
        'options': ['Haan, bataiye', 'Nahi, aage badhen'],
        'next_step': 'fee_structure',
        'is_optional': True
    },
    'fee_structure': {
        'id': 'fee_structure',
        'question': 'Fee Structure ki jaankari:\n\n📚 Tuition Fee: ₹60,000\n🚌 Bus Fee: ₹10,000\n💰 Total Annual Fees: ₹70,000\n\nYeh fees 3 installments mein banti hai:\n• 1st Installment: ₹30,000 (admission ke samay)\n• 2nd Installment: ₹20,000 (first semester ke baad)\n• 3rd Installment: ₹20,000 (second semester ke baad)\n\nKya aap hostel aur training facilities ke bare mein jaanna chahte hain?',
        'options': ['Haan', 'Nahi'],
        'next_step': 'hostel_facilities',
        'is_optional': True
    },
    'hostel_facilities': {
        'id': 'hostel_facilities',
        'question': 'Hostel aur Training Facilities:\n\n🏠 Hostel Facilities:\n• 24x7 paani aur bijli\n• CCTV nigrani suraksha ke liye\n• Warden hamesha uplabdh\n\n🏥 Training: Hospital training included hai jahan students ko real patients ke saath kaam karne ka mauka milta hai.\n\nKya aap college location ke bare mein jaanna chahte hain?',
        'options': ['Haan', 'Nahi'],
        'next_step': 'location',
        'is_optional': True
    },
    'location': {
        'id': 'location',
        'question': '📍 College Location: Hamara college Delhi mein sthit hai. Yeh ek behtarin location hai jo students ke liye suvidhaajanak hai. Kya aap surrounding area ke bare mein aur jaanna chahte hain?',
        'options': ['Haan', 'Nahi'],
        'next_step': 'recognition',
        'is_optional': True
    },
    'recognition': {
        'id': 'recognition',
        'question': ' Recognition aur Accreditation:\n\nHamara college Indian Nursing Council (INC) Delhi dwara manyata prapt hai. Yeh ek bahut mahattvapurn accreditation hai jo aapki degree ki value badhata hai.\n\nKya aap iske bare mein aur jaanna chahte hain?',
        'options': ['Haan', 'Nahi'],
        'next_step': 'clinical_training',
        'is_optional': True
    },
    'clinical_training': {
        'id': 'clinical_training',
        'question': '🏥 Clinical Training Locations:\n\n• District Hospital (Backundpur)\n• Community Health Centers\n• Regional Hospital (Chartha)\n• Ranchi Neurosurgery and Allied Science Hospital (Ranchi, Jharkhand)\n\nYe sabhi locations aapko practical experience dene ke liye hain. Kya aap scholarship options ke bare mein jaanna chahte hain?',
        'options': ['Haan', 'Nahi'],
        'next_step': 'scholarships',
        'is_optional': True
    },
    'scholarships': {
        'id': 'scholarships',
        'question': '🎓 Scholarship Options:\n\n• Government Post-Matric Scholarship: ₹18,000-₹23,000\n• Labour Ministry Scholarships: ₹40,000-₹48,000 (Labour Registration wale students ke liye)\n\nKya aap seats availability ke bare mein jaanna chahte hain?',
        'options': ['Haan', 'Nahi'],
        'next_step': 'seats_available',
        'is_optional': True
    },
    'seats_available': {
        'id': 'seats_available',
        'question': '💺 Total Seats Available: Hamare nursing program mein kul 60 seats uplabdh hain.\n\nKya aap complete eligibility criteria ke bare mein jaanna chahte hain?',
        'options': ['Haan', 'Nahi'],
        'next_step': 'eligibility_criteria',
        'is_optional': True
    },
    'eligibility_criteria': {
        'id': 'eligibility_criteria',
        'question': '📋 Admission Eligibility Criteria:\n\n• 12th grade mein Biology hona avashyak\n• PNT Exam pass karna zaroori\n• Age: 17 se 35 years\n\nYeh sabhi jaankari thi! Kya aap koi aur sawal poochna chahte hain?',
        'options': ['Haan', 'Nahi'],
        'next_step': 'end'
    },
    'end': {
        'id': 'end',
        'question': 'Dhanyawad! Agar aapko aur koi jaankari chahiye to kripya sampark karen. Aapka din shubh ho! 🙏',
        'options': [],
        'next_step': ''
    }
}

def is_positive_response(response):
    positive_responses = ['haan', 'yes', 'han', 'bataiye', 'kya hai', 'tell me more', 'batao', 'haan, bataiye', 'haan, biology padhi hai']
    return any(positive.lower() in response.lower() for positive in positive_responses)

def is_negative_response(response):
    negative_responses = ['nahi', 'no', 'nahi, biology nahi padhi', 'nahi, aage badhen','exit','mujhe exit karna ha']
    return any(negative.lower() in response.lower() for negative in negative_responses)

@app.route('/')
def login():
    if 'user' in session:
        return redirect(url_for('chat'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def handle_login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Simple authentication (in production, use proper authentication)
    if username == 'admin' and password == 'password':
        session['user'] = username
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Invalid username or password'})

@app.route('/chat')
def chat():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # Initialize chat session
    if 'chat_state' not in session:
        session['chat_state'] = {
            'current_step': 'welcome',
            'messages': [],
            'step_history': [],
            'user_responses': {},
            'is_completed': False
        }
    
    return render_template('chat.html', username=session['user'])

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user_message = request.json.get('message', '').strip()
    chat_state = session.get('chat_state', {})
    
    if not user_message:
        return jsonify({'error': 'Empty message'}), 400
    
    # Add user message to chat history
    chat_state['messages'].append({
        'id': len(chat_state['messages']) + 1,
        'text': user_message,
        'sender': 'user',
        'timestamp': datetime.now().strftime('%H:%M')
    })
    
    current_step = chat_state['current_step']
    current_step_data = CHAT_STEPS.get(current_step, {})
    
    # Handle negative responses
    if is_negative_response(user_message):
        if current_step == 'eligibility' and 'biology nahi padhi' in user_message.lower():
            chat_state['current_step'] = 'biology_required'
            chat_state['step_history'].append(current_step)
            chat_state['user_responses'][current_step] = user_message
            
            bot_response = CHAT_STEPS['biology_required']['question']
        else:
            # Polite exit for other negative responses
            bot_response = 'Koi baat nahi! Agar bhavishya mein koi sawal ho to kripya sampark karen. Dhanyawad! 🙏'
            chat_state['is_completed'] = True
    
    # Handle positive responses
    elif is_positive_response(user_message) or current_step_data.get('is_optional', False):
        next_step = current_step_data.get('next_step')
        if next_step and next_step != 'end':
            chat_state['current_step'] = next_step
            chat_state['step_history'].append(current_step)
            chat_state['user_responses'][current_step] = user_message
            
            bot_response = CHAT_STEPS[next_step]['question']
        else:
            # End conversation
            bot_response = CHAT_STEPS['end']['question']
            chat_state['is_completed'] = True
    else:
        # Default response for unclear input
        bot_response = 'Maaf kijiye, main samajh nahi paya. Kripya "Haan" ya "Nahi" mein jawab dijiye.'
    
    # Add bot response to chat history
    chat_state['messages'].append({
        'id': len(chat_state['messages']) + 1,
        'text': bot_response,
        'sender': 'bot',
        'timestamp': datetime.now().strftime('%H:%M')
    })
    
    session['chat_state'] = chat_state
    
    return jsonify({
        'bot_response': bot_response,
        'current_step': chat_state['current_step'],
        'options': CHAT_STEPS.get(chat_state['current_step'], {}).get('options', []),
        'is_completed': chat_state['is_completed'],
        'can_go_back': len(chat_state['step_history']) > 0 and not chat_state['is_completed']
    })

@app.route('/get_initial_message')
def get_initial_message():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    chat_state = session.get('chat_state', {})
    current_step = chat_state.get('current_step', 'welcome')
    
    return jsonify({
        'bot_response': CHAT_STEPS[current_step]['question'],
        'options': CHAT_STEPS[current_step].get('options', []),
        'current_step': current_step,
        'messages': chat_state.get('messages', [])
    })

@app.route('/go_back', methods=['POST'])
def go_back():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    chat_state = session.get('chat_state', {})
    
    if chat_state['step_history'] and not chat_state['is_completed']:
        previous_step = chat_state['step_history'].pop()
        chat_state['current_step'] = previous_step
        
        # Remove last two messages (bot and user)
        if len(chat_state['messages']) >= 2:
            chat_state['messages'] = chat_state['messages'][:-2]
        
        session['chat_state'] = chat_state
        
        return jsonify({
            'success': True,
            'current_step': previous_step,
            'bot_response': CHAT_STEPS[previous_step]['question'],
            'options': CHAT_STEPS[previous_step].get('options', [])
        })
    
    return jsonify({'success': False})

@app.route('/restart_chat', methods=['POST'])
def restart_chat():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    session['chat_state'] = {
        'current_step': 'welcome',
        'messages': [],
        'step_history': [],
        'user_responses': {},
        'is_completed': False
    }
    
    return jsonify({
        'success': True,
        'bot_response': CHAT_STEPS['welcome']['question'],
        'options': CHAT_STEPS['welcome']['options']
    })


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=8000)