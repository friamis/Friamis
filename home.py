"""
FRIAMIS - Application de messagerie en Python avec Streamlit
Installation: pip install streamlit supabase pandas plotly
Lancement: streamlit run friamis.py
"""

import streamlit as st
from supabase import create_client, Client
import os
from datetime import datetime, timedelta
import time
from typing import Optional, List, Dict
import base64

# =====================================================
# CONFIGURATION SUPABASE
# =====================================================

SUPABASE_URL = os.getenv("SUPABASE_URL", "YOUR_SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", "YOUR_SUPABASE_ANON_KEY")

try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error(f"Erreur connexion Supabase: {e}")

# =====================================================
# CONFIGURATION STREAMLIT
# =====================================================

st.set_page_config(
    page_title="Friamis - Messagerie",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Custom pour un design moderne
st.markdown("""
<style>
    /* Style général */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Container principal */
    .main-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    
    /* Messages */
    .message-own {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        max-width: 70%;
        margin-left: auto;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    .message-other {
        background: #f0f2f5;
        color: #1c1e21;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        max-width: 70%;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* Chat bubble */
    .chat-item {
        padding: 16px;
        border-radius: 12px;
        margin: 8px 0;
        cursor: pointer;
        transition: all 0.3s;
        background: white;
        border: 2px solid transparent;
    }
    
    .chat-item:hover {
        background: #f8f9fa;
        border-color: #667eea;
        transform: translateX(4px);
    }
    
    .chat-item-active {
        background: #e8eaf6;
        border-color: #667eea;
    }
    
    /* Boutons */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
    }
    
    /* Input */
    .stTextInput input, .stTextArea textarea {
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        padding: 12px;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Badge */
    .badge {
        background: #667eea;
        color: white;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
    
    /* Avatar */
    .avatar {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Status online */
    .status-online {
        width: 12px;
        height: 12px;
        background: #4caf50;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Notification */
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        padding: 16px 24px;
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
    }
    
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# =====================================================
# GESTION DE L'ÉTAT
# =====================================================

# Initialiser session state
if 'user' not in st.session_state:
    st.session_state.user = None
if 'selected_chat' not in st.session_state:
    st.session_state.selected_chat = None
if 'conversations' not in st.session_state:
    st.session_state.conversations = []
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'contacts' not in st.session_state:
    st.session_state.contacts = []
if 'notification' not in st.session_state:
    st.session_state.notification = None
if 'muted_chats' not in st.session_state:
    st.session_state.muted_chats = []

# =====================================================
# FONCTIONS UTILITAIRES
# =====================================================

def show_notification(message: str, type: str = "info"):
    """Afficher une notification"""
    st.session_state.notification = {"message": message, "type": type}

def format_time(dt: datetime) -> str:
    """Formater le temps de manière lisible"""
    now = datetime.now()
    diff = now - dt
    
    if diff.seconds < 60:
        return "À l'instant"
    elif diff.seconds < 3600:
        return f"{diff.seconds // 60}min"
    elif diff.seconds < 86400:
        return f"{diff.seconds // 3600}h"
    elif diff.days < 7:
        return f"{diff.days}j"
    else:
        return dt.strftime("%d/%m")

def format_message_time(dt: datetime) -> str:
    """Formater l'heure d'un message"""
    return dt.strftime("%H:%M")

# =====================================================
# FONCTIONS SUPABASE
# =====================================================

def sign_up(email: str, password: str, username: str, display_name: str) -> bool:
    """Inscription utilisateur"""
    try:
        result = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "username": username,
                    "display_name": display_name
                }
            }
        })
        
        if result.user:
            show_notification("Inscription réussie !", "success")
            return True
        return False
    except Exception as e:
        show_notification(f"Erreur inscription: {str(e)}", "error")
        return False

def sign_in(email: str, password: str) -> bool:
    """Connexion utilisateur"""
    try:
        result = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if result.user:
            # Récupérer le profil
            profile = supabase.table("profiles").select("*").eq("id", result.user.id).execute()
            if profile.data:
                st.session_state.user = {
                    "id": result.user.id,
                    "email": result.user.email,
                    **profile.data[0]
                }
                show_notification("Connexion réussie !", "success")
                return True
        return False
    except Exception as e:
        show_notification(f"Erreur connexion: {str(e)}", "error")
        return False

def sign_out():
    """Déconnexion"""
    try:
        supabase.auth.sign_out()
        st.session_state.user = None
        st.session_state.selected_chat = None
        st.session_state.messages = []
        show_notification("Déconnexion réussie", "success")
    except Exception as e:
        show_notification(f"Erreur déconnexion: {str(e)}", "error")

def load_conversations():
    """Charger les conversations de l'utilisateur"""
    if not st.session_state.user:
        return
    
    try:
        result = supabase.rpc('get_user_conversations', {
            'user_id_param': st.session_state.user['id']
        }).execute()
        
        st.session_state.conversations = result.data or []
    except Exception as e:
        show_notification(f"Erreur chargement conversations: {str(e)}", "error")

def load_contacts():
    """Charger la liste des contacts"""
    if not st.session_state.user:
        return
    
    try:
        result = supabase.table("profiles").select("*").neq("id", st.session_state.user['id']).execute()
        st.session_state.contacts = result.data or []
    except Exception as e:
        show_notification(f"Erreur chargement contacts: {str(e)}", "error")

def load_messages(conversation_id: str):
    """Charger les messages d'une conversation"""
    try:
        result = supabase.table("messages").select("""
            *,
            sender:profiles!sender_id(username, display_name, avatar_url),
            reactions(emoji, user_id)
        """).eq("conversation_id", conversation_id).order("created_at").execute()
        
        st.session_state.messages = result.data or []
    except Exception as e:
        show_notification(f"Erreur chargement messages: {str(e)}", "error")

def send_message(content: str, content_type: str = "text", file_url: Optional[str] = None, reply_to: Optional[str] = None):
    """Envoyer un message"""
    if not st.session_state.selected_chat or not content.strip():
        return False
    
    try:
        message_data = {
            "conversation_id": st.session_state.selected_chat['id'],
            "sender_id": st.session_state.user['id'],
            "content": content,
            "content_type": content_type,
            "file_url": file_url,
            "reply_to": reply_to
        }
        
        result = supabase.table("messages").insert(message_data).execute()
        
        if result.data:
            show_notification("Message envoyé", "success")
            load_messages(st.session_state.selected_chat['id'])
            return True
        return False
    except Exception as e:
        show_notification(f"Erreur envoi message: {str(e)}", "error")
        return False

def create_conversation(contact_id: str, contact_name: str, contact_avatar: str):
    """Créer une nouvelle conversation"""
    try:
        # Créer la conversation
        conv_result = supabase.table("conversations").insert({
            "kind": "dm",
            "name": contact_name,
            "avatar_url": contact_avatar,
            "created_by": st.session_state.user['id']
        }).execute()
        
        if not conv_result.data:
            return False
        
        conversation_id = conv_result.data[0]['id']
        
        # Ajouter les membres
        supabase.table("conversation_members").insert([
            {"conversation_id": conversation_id, "user_id": st.session_state.user['id']},
            {"conversation_id": conversation_id, "user_id": contact_id}
        ]).execute()
        
        show_notification("Conversation créée", "success")
        load_conversations()
        return True
    except Exception as e:
        show_notification(f"Erreur création conversation: {str(e)}", "error")
        return False

def delete_message(message_id: str):
    """Supprimer un message"""
    try:
        supabase.table("messages").delete().eq("id", message_id).execute()
        show_notification("Message supprimé", "success")
        load_messages(st.session_state.selected_chat['id'])
    except Exception as e:
        show_notification(f"Erreur suppression: {str(e)}", "error")

def add_reaction(message_id: str, emoji: str):
    """Ajouter une réaction à un message"""
    try:
        supabase.table("reactions").upsert({
            "message_id": message_id,
            "user_id": st.session_state.user['id'],
            "emoji": emoji
        }).execute()
        load_messages(st.session_state.selected_chat['id'])
    except Exception as e:
        show_notification(f"Erreur ajout réaction: {str(e)}", "error")

# =====================================================
# INTERFACE - PAGE AUTHENTIFICATION
# =====================================================

def render_auth_page():
    """Afficher la page d'authentification"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div style='text-align: center; padding: 2rem;'>", unsafe_allow_html=True)
        st.markdown("<h1 style='font-size: 4rem;'>💬</h1>", unsafe_allow_html=True)
        st.markdown("<h1 style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Friamis</h1>", unsafe_allow_html=True)
        st.markdown("<p style='color: #666;'>Messagerie temps réel sécurisée</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Tabs pour login/signup
        tab1, tab2 = st.tabs(["🔐 Connexion", "✨ Inscription"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("📧 Email", placeholder="votre@email.com")
                password = st.text_input("🔒 Mot de passe", type="password", placeholder="••••••••")
                submit = st.form_submit_button("Se connecter", use_container_width=True)
                
                if submit:
                    if email and password:
                        if sign_in(email, password):
                            st.rerun()
                    else:
                        st.error("Veuillez remplir tous les champs")
        
        with tab2:
            with st.form("signup_form"):
                username = st.text_input("👤 Nom d'utilisateur", placeholder="username")
                display_name = st.text_input("✨ Nom d'affichage", placeholder="John Doe")
                email = st.text_input("📧 Email", placeholder="votre@email.com")
                password = st.text_input("🔒 Mot de passe", type="password", placeholder="••••••••")
                submit = st.form_submit_button("S'inscrire", use_container_width=True)
                
                if submit:
                    if username and display_name and email and password:
                        if sign_up(email, password, username, display_name):
                            st.rerun()
                    else:
                        st.error("Veuillez remplir tous les champs")

# =====================================================
# INTERFACE - PAGE PRINCIPALE (CHAT)
# =====================================================

def render_chat_page():
    """Afficher la page de chat principale"""
    
    # Charger les données
    if not st.session_state.conversations:
        load_conversations()
    if not st.session_state.contacts:
        load_contacts()
    
    # Sidebar - Liste des conversations
    with st.sidebar:
        # Header utilisateur
        st.markdown(f"""
        <div style='padding: 1rem; text-align: center; background: rgba(255,255,255,0.1); border-radius: 12px; margin-bottom: 1rem;'>
            <div style='font-size: 3rem;'>{st.session_state.user.get('avatar_url', '😊')}</div>
            <div style='font-weight: 600; margin-top: 0.5rem;'>{st.session_state.user.get('display_name', 'Utilisateur')}</div>
            <div style='font-size: 0.9rem; opacity: 0.8;'>@{st.session_state.user.get('username', 'user')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Recherche
        search_query = st.text_input("🔍 Rechercher", placeholder="Rechercher une conversation...")
        
        # Bouton nouvelle conversation
        if st.button("➕ Nouvelle conversation", use_container_width=True):
            st.session_state.show_new_chat = True
        
        # Modal nouvelle conversation
        if st.session_state.get('show_new_chat', False):
            st.markdown("### 👥 Contacts")
            
            if st.session_state.contacts:
                for contact in st.session_state.contacts:
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.markdown(f"<div style='font-size: 2rem;'>{contact.get('avatar_url', '👤')}</div>", unsafe_allow_html=True)
                    with col2:
                        if st.button(f"{contact['display_name']}", key=f"contact_{contact['id']}", use_container_width=True):
                            create_conversation(contact['id'], contact['display_name'], contact.get('avatar_url', '👤'))
                            st.session_state.show_new_chat = False
                            st.rerun()
            else:
                st.info("Aucun contact disponible")
            
            if st.button("❌ Fermer", use_container_width=True):
                st.session_state.show_new_chat = False
                st.rerun()
        
        # Liste des conversations
        st.markdown("### 💬 Conversations")
        
        filtered_convs = [c for c in st.session_state.conversations if search_query.lower() in c.get('name', '').lower()]
        
        if filtered_convs:
            for conv in filtered_convs:
                is_selected = st.session_state.selected_chat and st.session_state.selected_chat['id'] == conv['id']
                
                if st.button(
                    f"{conv.get('avatar_url', '💬')} {conv.get('name', 'Conversation')}",
                    key=f"conv_{conv['id']}",
                    use_container_width=True,
                    type="primary" if is_selected else "secondary"
                ):
                    st.session_state.selected_chat = conv
                    load_messages(conv['id'])
                    st.rerun()
        else:
            st.info("Aucune conversation")
        
        # Bouton déconnexion
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 Déconnexion", use_container_width=True):
            sign_out()
            st.rerun()
    
    # Zone principale - Messages
    if st.session_state.selected_chat:
        # Header du chat
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.markdown(f"""
            <div style='display: flex; align-items: center; gap: 1rem;'>
                <div style='font-size: 3rem;'>{st.session_state.selected_chat.get('avatar_url', '💬')}</div>
                <div>
                    <h3 style='margin: 0;'>{st.session_state.selected_chat.get('name', 'Conversation')}</h3>
                    <p style='margin: 0; color: #666; font-size: 0.9rem;'>
                        {st.session_state.selected_chat.get('kind', 'dm') == 'dm' ? 'Conversation privée' : 'Groupe'}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if st.button("📞 Appeler"):
                show_notification("Fonction appel bientôt disponible", "info")
        
        with col3:
            is_muted = st.session_state.selected_chat['id'] in st.session_state.muted_chats
            if st.button("🔕" if is_muted else "🔔"):
                if is_muted:
                    st.session_state.muted_chats.remove(st.session_state.selected_chat['id'])
                    show_notification("Notifications activées", "success")
                else:
                    st.session_state.muted_chats.append(st.session_state.selected_chat['id'])
                    show_notification("Notifications désactivées", "success")
        
        st.divider()
        
        # Zone de messages
        message_container = st.container(height=500)
        
        with message_container:
            if st.session_state.messages:
                for msg in st.session_state.messages:
                    is_own = msg['sender_id'] == st.session_state.user['id']
                    
                    col1, col2 = st.columns([1, 1] if is_own else [1, 1])
                    
                    with (col2 if is_own else col1):
                        # Message bubble
                        message_class = "message-own" if is_own else "message-other"
                        
                        st.markdown(f"""
                        <div class='{message_class}'>
                            <div>{msg['content']}</div>
                            <div style='font-size: 0.75rem; opacity: 0.7; margin-top: 4px;'>
                                {format_message_time(datetime.fromisoformat(msg['created_at'].replace('Z', '+00:00')))}
                                {'✓✓' if is_own else ''}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Réactions
                        if msg.get('reactions'):
                            reactions_html = ""
                            reaction_counts = {}
                            for r in msg['reactions']:
                                emoji = r['emoji']
                                reaction_counts[emoji] = reaction_counts.get(emoji, 0) + 1
                            
                            for emoji, count in reaction_counts.items():
                                reactions_html += f'<span style="background: white; padding: 2px 8px; border-radius: 12px; margin: 2px; display: inline-block;">{emoji} {count}</span>'
                            
                            st.markdown(f"<div style='margin-top: 4px;'>{reactions_html}</div>", unsafe_allow_html=True)
                        
                        # Boutons d'action
                        action_col1, action_col2, action_col3 = st.columns(3)
                        
                        with action_col1:
                            if st.button("👍", key=f"like_{msg['id']}", help="J'aime"):
                                add_reaction(msg['id'], "👍")
                                st.rerun()
                        
                        with action_col2:
                            if st.button("❤️", key=f"love_{msg['id']}", help="Adore"):
                                add_reaction(msg['id'], "❤️")
                                st.rerun()
                        
                        with action_col3:
                            if is_own and st.button("🗑️", key=f"delete_{msg['id']}", help="Supprimer"):
                                delete_message(msg['id'])
                                st.rerun()
            else:
                st.info("Aucun message. Envoyez le premier !")
        
        st.divider()
        
        # Zone d'envoi de message
        with st.form("message_form", clear_on_submit=True):
            col1, col2 = st.columns([5, 1])
            
            with col1:
                message_input = st.text_area(
                    "Message",
                    placeholder="Écrivez votre message...",
                    label_visibility="collapsed",
                    height=80
                )
            
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                send_button = st.form_submit_button("📤 Envoyer", use_container_width=True)
            
            if send_button and message_input.strip():
                if send_message(message_input):
                    st.rerun()
    
    else:
        # Aucun chat sélectionné
        st.markdown("""
        <div style='display: flex; flex-direction: column; align-items: center; justify-content: center; height: 60vh;'>
            <div style='font-size: 6rem; opacity: 0.3;'>💬</div>
            <h2 style='color: #999; margin-top: 1rem;'>Sélectionnez une conversation</h2>
            <p style='color: #bbb;'>Choisissez un contact pour commencer à discuter</p>
        </div>
        """, unsafe_allow_html=True)

# =====================================================
# NOTIFICATIONS
# =====================================================

def render_notifications():
    """Afficher les notifications"""
    if st.session_state.notification:
        notif = st.session_state.notification
        icon = "✅" if notif['type'] == "success" else "❌" if notif['type'] == "error" else "ℹ️"
        
        st.markdown(f"""
        <div class='notification'>
            <div style='display: flex; align-items: center; gap: 12px;'>
                <span style='font-size: 1.5rem;'>{icon}</span>
                <span style='font-weight: 500;'>{notif['message']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Auto-clear après 3 secondes
        time.sleep(3)
        st.session_state.notification = None

# =====================================================
# APPLICATION PRINCIPALE
# =====================================================

def main():
    """Point d'entrée principal de l'application"""
    
    # Afficher les notifications
    render_notifications()
    
    # Router selon l'état de connexion
    if st.session_state.user is None:
        render_auth_page()
    else:
        render_chat_page()

if __name__ == "__main__":
    main()
