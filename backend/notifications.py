import os
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional

class NotificationService:
    """Service for sending notifications via SMS, WhatsApp, and push notifications"""
    
    def __init__(self):
        # Twilio configuration for SMS/WhatsApp
        self.twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID', 'your-twilio-account-sid')
        self.twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN', 'your-twilio-auth-token')
        self.twilio_phone_number = os.getenv('TWILIO_PHONE_NUMBER', '+1234567890')
        
        # Firebase configuration for push notifications
        self.firebase_server_key = os.getenv('FIREBASE_SERVER_KEY', 'your-firebase-server-key')
        self.firebase_project_id = os.getenv('FIREBASE_PROJECT_ID', 'your-firebase-project-id')
        
        # Notification templates
        self.templates = {
            'high_risk': {
                'en': '🚨 HIGH RISK ALERT: Your {crop} crop in {region} shows {risk_level} risk. Predicted yield: {predicted_yield} tons/ha. Check recommendations immediately.',
                'hi': '🚨 उच्च जोखिम चेतावनी: आपकी {crop} फसल {region} में {risk_level} जोखिम दिखा रही है। अनुमानित उपज: {predicted_yield} टन/हेक्टेयर। तुरंत सिफारिशें देखें।',
                'ta': '🚨 உயர் ஆபத்து எச்சரிக்கை: உங்கள் {crop} பயிர் {region} இல் {risk_level} ஆபத்து காட்டுகிறது. கணிக்கப்பட்ட விளைச்சல்: {predicted_yield} டன்/ஹெக்டேர். உடனடியாக பரிந்துரைகளை பாருங்கள்.'
            },
            'weather_alert': {
                'en': '🌦️ WEATHER ALERT: {weather_desc} in {region}. Temperature: {temp}°C, Rainfall: {rainfall}mm. Adjust farming practices accordingly.',
                'hi': '🌦️ मौसम चेतावनी: {region} में {weather_desc}। तापमान: {temp}°C, वर्षा: {rainfall}mm। तदनुसार खेती के तरीकों को समायोजित करें।',
                'ta': '🌦️ வானிலை எச்சரிக்கை: {region} இல் {weather_desc}। வெப்பநிலை: {temp}°C, மழைப்பொழிவு: {rainfall}mm. அதற்கேற்ப விவசாய நடைமுறைகளை சரிசெய்யவும்.'
            },
            'yield_update': {
                'en': '📊 YIELD UPDATE: Your {crop} crop prediction updated. New yield: {predicted_yield} tons/ha. Risk level: {risk_level}.',
                'hi': '📊 उपज अपडेट: आपकी {crop} फसल की भविष्यवाणी अपडेट की गई। नई उपज: {predicted_yield} टन/हेक्टेयर। जोखिम स्तर: {risk_level}।',
                'ta': '📊 விளைச்சல் புதுப்பிப்பு: உங்கள் {crop} பயிர் கணிப்பு புதுப்பிக்கப்பட்டது. புதிய விளைச்சல்: {predicted_yield} டன்/ஹெக்டேர். ஆபத்து நிலை: {risk_level}.'
            }
        }
    
    def send_sms(self, phone_number: str, message: str) -> Dict:
        """Send SMS using Twilio"""
        try:
            if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_phone_number]):
                return {'success': False, 'error': 'Twilio credentials not configured'}
            
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages.json"
            payload = {
                'From': self.twilio_phone_number,
                'To': phone_number,
                'Body': message
            }
            
            response = requests.post(
                url,
                data=payload,
                auth=(self.twilio_account_sid, self.twilio_auth_token),
                timeout=10
            )
            
            if response.status_code == 201:
                return {'success': True, 'message_id': response.json().get('sid')}
            else:
                return {'success': False, 'error': f'Twilio API error: {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_whatsapp(self, phone_number: str, message: str) -> Dict:
        """Send WhatsApp message using Twilio"""
        try:
            if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_phone_number]):
                return {'success': False, 'error': 'Twilio credentials not configured'}
            
            # Format phone number for WhatsApp (remove + and add whatsapp: prefix)
            whatsapp_number = f"whatsapp:{phone_number.replace('+', '')}"
            from_number = f"whatsapp:{self.twilio_phone_number.replace('+', '')}"
            
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_account_sid}/Messages.json"
            payload = {
                'From': from_number,
                'To': whatsapp_number,
                'Body': message
            }
            
            response = requests.post(
                url,
                data=payload,
                auth=(self.twilio_account_sid, self.twilio_auth_token),
                timeout=10
            )
            
            if response.status_code == 201:
                return {'success': True, 'message_id': response.json().get('sid')}
            else:
                return {'success': False, 'error': f'Twilio API error: {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_push_notification(self, fcm_token: str, title: str, body: str, data: Dict = None) -> Dict:
        """Send push notification using Firebase"""
        try:
            if not self.firebase_server_key:
                return {'success': False, 'error': 'Firebase credentials not configured'}
            
            url = 'https://fcm.googleapis.com/fcm/send'
            headers = {
                'Authorization': f'key={self.firebase_server_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'to': fcm_token,
                'notification': {
                    'title': title,
                    'body': body,
                    'icon': '🌾',
                    'click_action': 'FLUTTER_NOTIFICATION_CLICK'
                },
                'data': data or {}
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') == 1:
                    return {'success': True, 'message_id': result.get('results', [{}])[0].get('message_id')}
                else:
                    return {'success': False, 'error': 'Firebase delivery failed'}
            else:
                return {'success': False, 'error': f'Firebase API error: {response.status_code}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def send_high_risk_alert(self, user_data: Dict, crop_data: Dict, language: str = 'en') -> Dict:
        """Send high-risk alert notification"""
        template = self.templates['high_risk'].get(language, self.templates['high_risk']['en'])
        
        message = template.format(
            crop=crop_data.get('crop_type', 'Unknown'),
            region=crop_data.get('region', 'Unknown'),
            risk_level=crop_data.get('risk_level', 'Unknown'),
            predicted_yield=crop_data.get('predicted_yield', 'Unknown')
        )
        
        results = {}
        
        # Send SMS if phone number available
        if user_data.get('phone'):
            results['sms'] = self.send_sms(user_data['phone'], message)
        
        # Send WhatsApp if phone number available
        if user_data.get('phone'):
            results['whatsapp'] = self.send_whatsapp(user_data['phone'], message)
        
        # Send push notification if FCM token available
        if user_data.get('fcm_token'):
            title = '🚨 High Risk Alert' if language == 'en' else \
                   '🚨 उच्च जोखिम चेतावनी' if language == 'hi' else '🚨 உயர் ஆபத்து எச்சரிக்கை'
            
            results['push'] = self.send_push_notification(
                user_data['fcm_token'],
                title,
                message
            )
        
        return results
    
    def send_weather_alert(self, user_data: Dict, weather_data: Dict, language: str = 'en') -> Dict:
        """Send weather alert notification"""
        template = self.templates['weather_alert'].get(language, self.templates['weather_alert']['en'])
        
        message = template.format(
            weather_desc=weather_data.get('weather_desc', 'Unknown'),
            region=user_data.get('region', 'Unknown'),
            temp=weather_data.get('temperature', 'Unknown'),
            rainfall=weather_data.get('rainfall', 'Unknown')
        )
        
        results = {}
        
        # Send SMS if phone number available
        if user_data.get('phone'):
            results['sms'] = self.send_sms(user_data['phone'], message)
        
        # Send push notification if FCM token available
        if user_data.get('fcm_token'):
            title = '🌦️ Weather Alert' if language == 'en' else \
                   '🌦️ मौसम चेतावनी' if language == 'hi' else '🌦️ வானிலை எச்சரிக்கை'
            
            results['push'] = self.send_push_notification(
                user_data['fcm_token'],
                title,
                message
            )
        
        return results
    
    def send_yield_update(self, user_data: Dict, crop_data: Dict, language: str = 'en') -> Dict:
        """Send yield update notification"""
        template = self.templates['yield_update'].get(language, self.templates['yield_update']['en'])
        
        message = template.format(
            crop=crop_data.get('crop_type', 'Unknown'),
            predicted_yield=crop_data.get('predicted_yield', 'Unknown'),
            risk_level=crop_data.get('risk_level', 'Unknown')
        )
        
        results = {}
        
        # Send SMS if phone number available
        if user_data.get('phone'):
            results['sms'] = self.send_sms(user_data['phone'], message)
        
        # Send push notification if FCM token available
        if user_data.get('fcm_token'):
            title = '📊 Yield Update' if language == 'en' else \
                   '📊 उपज अपडेट' if language == 'hi' else '📊 விளைச்சல் புதுப்பிப்பு'
            
            results['push'] = self.send_push_notification(
                user_data['fcm_token'],
                title,
                message
            )
        
        return results
    
    def send_bulk_notifications(self, users: List[Dict], message: str, notification_type: str = 'general') -> Dict:
        """Send bulk notifications to multiple users"""
        results = {
            'total_users': len(users),
            'successful': 0,
            'failed': 0,
            'details': {}
        }
        
        for user in users:
            user_results = {}
            
            # Send SMS
            if user.get('phone'):
                user_results['sms'] = self.send_sms(user['phone'], message)
                if user_results['sms']['success']:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
            
            # Send push notification
            if user.get('fcm_token'):
                user_results['push'] = self.send_push_notification(
                    user['fcm_token'],
                    '🌾 Crop Advisory',
                    message
                )
                if user_results['push']['success']:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
            
            results['details'][user.get('id', 'unknown')] = user_results
        
        return results

# Global notification service instance
notification_service = NotificationService()
