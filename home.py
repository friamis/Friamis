import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, Send, Paperclip, LogOut, Search, Plus, X, Users, Phone, Video, MoreVertical, Smile, Check, CheckCheck, Mic, StopCircle, Play, Pause, ThumbsUp, Heart, Laugh, AlertCircle, Trash2, Edit2, Reply, Copy, Bell, BellOff, Image as ImageIcon, File } from 'lucide-react';

// Simulation du client Supabase avec stockage persistant
const createSupabaseClient = () => ({
  auth: {
    signUp: async ({ email, password }) => {
      const user = { id: Math.random().toString(36), email };
      localStorage.setItem('user', JSON.stringify(user));
      return { data: { user }, error: null };
    },
    signInWithPassword: async ({ email, password }) => {
      const user = { id: Math.random().toString(36), email };
      localStorage.setItem('user', JSON.stringify(user));
      return { data: { user }, error: null };
    },
    signOut: async () => {
      localStorage.removeItem('user');
      return { error: null };
    },
    getSession: async () => {
      const user = localStorage.getItem('user');
      return { data: { session: user ? { user: JSON.parse(user) } : null } };
    }
  }
});

const supabase = createSupabaseClient();

const Friamais = () => {
  // États principaux
  const [currentView, setCurrentView] = useState('auth');
  const [authMode, setAuthMode] = useState('login');
  const [user, setUser] = useState(null);
  const [selectedChat, setSelectedChat] = useState(null);
  const [messageInput, setMessageInput] = useState('');
  const [showNewChat, setShowNewChat] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);
  const [editingMessage, setEditingMessage] = useState(null);
  const [replyingTo, setReplyingTo] = useState(null);
  const [selectedMessage, setSelectedMessage] = useState(null);
  
  // États notifications et enregistrement audio
  const [notifications, setNotifications] = useState([]);
  const [mutedChats, setMutedChats] = useState([]);
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioBlob, setAudioBlob] = useState(null);
  const [playingAudio, setPlayingAudio] = useState(null);
  
  // Données
  const [chats, setChats] = useState([]);
  const [messages, setMessages] = useState([]);
  const [contacts, setContacts] = useState([]);
  
  // Formulaire auth
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    username: '',
    displayName: ''
  });
  
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const imageInputRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const recordingIntervalRef = useRef(null);
  const audioRef = useRef(null);

  // Emojis disponibles
  const emojis = ['😊', '😂', '❤️', '👍', '🎉', '😍', '🔥', '👏', '😢', '😮', '🤔', '💯'];
  const reactions = [
    { emoji: '👍', label: 'J\'aime' },
    { emoji: '❤️', label: 'Adore' },
    { emoji: '😂', label: 'Drôle' },
    { emoji: '😮', label: 'Wow' },
    { emoji: '😢', label: 'Triste' }
  ];

  // Charger les données mockées
  useEffect(() => {
    if (user) {
      setChats([
        {
          id: '1',
          name: 'Sophie Martin',
          type: 'dm',
          avatar: '👩',
          lastMessage: 'Salut ! Comment ça va ?',
          lastMessageTime: new Date(Date.now() - 300000),
          unread: 2,
          online: true
        },
        {
          id: '2',
          name: 'Équipe Dev',
          type: 'group',
          avatar: '💻',
          lastMessage: 'Pierre: Meeting à 15h',
          lastMessageTime: new Date(Date.now() - 3600000),
          unread: 0,
          members: 5
        },
        {
          id: '3',
          name: 'Jules Dupont',
          type: 'dm',
          avatar: '👨',
          lastMessage: 'On se voit demain ?',
          lastMessageTime: new Date(Date.now() - 7200000),
          unread: 1,
          online: false
        },
        {
          id: '4',
          name: 'Famille ❤️',
          type: 'group',
          avatar: '👨‍👩‍👧‍👦',
          lastMessage: 'Maman: N\'oubliez pas dimanche !',
          lastMessageTime: new Date(Date.now() - 86400000),
          unread: 0,
          members: 4
        }
      ]);

      setContacts([
        { id: '1', username: 'sophie_m', displayName: 'Sophie Martin', avatar: '👩', online: true },
        { id: '2', username: 'jules_d', displayName: 'Jules Dupont', avatar: '👨', online: false },
        { id: '3', username: 'marie_l', displayName: 'Marie Laurent', avatar: '👧', online: true },
        { id: '4', username: 'pierre_b', displayName: 'Pierre Bernard', avatar: '🧑', online: true }
      ]);
    }
  }, [user]);

  // Charger les messages du chat sélectionné
  useEffect(() => {
    if (selectedChat) {
      const mockMessages = [
        {
          id: '1',
          senderId: '2',
          content: 'Salut ! Comment ça va ?',
          timestamp: new Date(Date.now() - 3600000),
          type: 'text',
          status: 'read',
          reactions: []
        },
        {
          id: '2',
          senderId: user.id,
          content: 'Très bien merci ! Et toi ?',
          timestamp: new Date(Date.now() - 3300000),
          type: 'text',
          status: 'read',
          reactions: [{ emoji: '👍', userId: '2', userName: 'Sophie' }]
        },
        {
          id: '3',
          senderId: '2',
          content: 'Super ! Tu es dispo ce soir pour un appel ?',
          timestamp: new Date(Date.now() - 3000000),
          type: 'text',
          status: 'read',
          reactions: []
        },
        {
          id: '4',
          senderId: user.id,
          content: 'Oui bien sûr, vers quelle heure ?',
          timestamp: new Date(Date.now() - 2700000),
          type: 'text',
          status: 'delivered',
          reactions: []
        },
        {
          id: '5',
          senderId: '2',
          content: '19h ça te va ?',
          timestamp: new Date(Date.now() - 2400000),
          type: 'text',
          status: 'sent',
          reactions: []
        }
      ];
      setMessages(mockMessages);
    }
  }, [selectedChat, user]);

  // Auto-scroll vers le bas
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Timer enregistrement audio
  useEffect(() => {
    if (isRecording) {
      recordingIntervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } else {
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
      }
      setRecordingTime(0);
    }
    return () => {
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
      }
    };
  }, [isRecording]);

  // Vérifier session au chargement
  useEffect(() => {
    const checkSession = async () => {
      const { data } = await supabase.auth.getSession();
      if (data.session) {
        setUser({
          id: data.session.user.id,
          email: data.session.user.email,
          username: 'demo_user',
          displayName: 'Demo User',
          avatar: '😊'
        });
        setCurrentView('chat');
      }
    };
    checkSession();
  }, []);

  // Gestion authentification
  const handleAuth = async () => {
    const { email, password, username, displayName } = formData;
    
    if (!email || !password) return;
    if (authMode === 'signup' && (!username || !displayName)) return;

    try {
      let result;
      if (authMode === 'signup') {
        result = await supabase.auth.signUp({ email, password });
      } else {
        result = await supabase.auth.signInWithPassword({ email, password });
      }

      if (!result.error) {
        setUser({
          id: result.data.user.id,
          email,
          username: authMode === 'signup' ? username : 'demo_user',
          displayName: authMode === 'signup' ? displayName : 'Demo User',
          avatar: '😊'
        });
        setCurrentView('chat');
      }
    } catch (error) {
      console.error('Auth error:', error);
    }
  };

  // Déconnexion
  const handleLogout = async () => {
    await supabase.auth.signOut();
    setUser(null);
    setCurrentView('auth');
    setSelectedChat(null);
    setMessages([]);
  };

  // Envoyer un message
  const handleSendMessage = () => {
    if ((!messageInput.trim() && !audioBlob) || !selectedChat) return;

    let newMessage;

    if (audioBlob) {
      newMessage = {
        id: Date.now().toString(),
        senderId: user.id,
        content: `Message vocal (${recordingTime}s)`,
        timestamp: new Date(),
        type: 'audio',
        audioUrl: URL.createObjectURL(audioBlob),
        duration: recordingTime,
        status: 'sent',
        reactions: []
      };
      setAudioBlob(null);
    } else if (editingMessage) {
      setMessages(messages.map(msg => 
        msg.id === editingMessage.id 
          ? { ...msg, content: messageInput, edited: true }
          : msg
      ));
      setEditingMessage(null);
      setMessageInput('');
      return;
    } else {
      newMessage = {
        id: Date.now().toString(),
        senderId: user.id,
        content: messageInput,
        timestamp: new Date(),
        type: 'text',
        status: 'sent',
        reactions: [],
        replyTo: replyingTo
      };
    }

    setMessages([...messages, newMessage]);
    setMessageInput('');
    setReplyingTo(null);

    // Mettre à jour le dernier message du chat
    setChats(chats.map(chat => 
      chat.id === selectedChat.id 
        ? { ...chat, lastMessage: newMessage.type === 'audio' ? '🎤 Message vocal' : messageInput, lastMessageTime: new Date() }
        : chat
    ));

    // Notification si chat muté
    if (!mutedChats.includes(selectedChat.id)) {
      addNotification(`Nouveau message de ${selectedChat.name}`);
    }
  };

  // Upload fichier
  const handleFileUpload = (e, type = 'file') => {
    const file = e.target.files?.[0];
    if (!file) return;

    const newMessage = {
      id: Date.now().toString(),
      senderId: user.id,
      content: file.name,
      timestamp: new Date(),
      type: type === 'image' ? 'image' : 'file',
      fileUrl: URL.createObjectURL(file),
      status: 'sent',
      reactions: []
    };

    setMessages([...messages, newMessage]);
    addNotification(`Fichier envoyé: ${file.name}`);
  };

  // Enregistrement audio
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      
      const chunks = [];
      mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        setAudioBlob(blob);
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Erreur enregistrement:', error);
      addNotification('Impossible d\'accéder au microphone', 'error');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const cancelRecording = () => {
    stopRecording();
    setAudioBlob(null);
    setRecordingTime(0);
  };

  // Lecture audio
  const toggleAudioPlay = (audioUrl) => {
    if (playingAudio === audioUrl) {
      audioRef.current?.pause();
      setPlayingAudio(null);
    } else {
      if (audioRef.current) {
        audioRef.current.src = audioUrl;
        audioRef.current.play();
        setPlayingAudio(audioUrl);
      }
    }
  };

  // Réactions
  const addReaction = (messageId, emoji) => {
    setMessages(messages.map(msg => {
      if (msg.id === messageId) {
        const existingReaction = msg.reactions.find(r => r.userId === user.id);
        if (existingReaction) {
          return {
            ...msg,
            reactions: msg.reactions.map(r => 
              r.userId === user.id ? { ...r, emoji } : r
            )
          };
        } else {
          return {
            ...msg,
            reactions: [...msg.reactions, { emoji, userId: user.id, userName: user.displayName }]
          };
        }
      }
      return msg;
    }));
    setSelectedMessage(null);
  };

  // Actions message
  const handleEditMessage = (message) => {
    setEditingMessage(message);
    setMessageInput(message.content);
    setSelectedMessage(null);
  };

  const handleReplyMessage = (message) => {
    setReplyingTo(message);
    setSelectedMessage(null);
  };

  const handleDeleteMessage = (messageId) => {
    setMessages(messages.filter(msg => msg.id !== messageId));
    setSelectedMessage(null);
    addNotification('Message supprimé');
  };

  const handleCopyMessage = (content) => {
    navigator.clipboard.writeText(content);
    setSelectedMessage(null);
    addNotification('Message copié');
  };

  // Notifications
  const addNotification = (message, type = 'info') => {
    const notification = {
      id: Date.now(),
      message,
      type,
      timestamp: new Date()
    };
    setNotifications(prev => [...prev, notification]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== notification.id));
    }, 3000);
  };

  // Mute/unmute chat
  const toggleMuteChat = (chatId) => {
    if (mutedChats.includes(chatId)) {
      setMutedChats(mutedChats.filter(id => id !== chatId));
      addNotification('Notifications activées');
    } else {
      setMutedChats([...mutedChats, chatId]);
      addNotification('Notifications désactivées');
    }
  };

  // Formater le temps
  const formatTime = (date) => {
    const now = new Date();
    const diff = now - new Date(date);
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'À l\'instant';
    if (minutes < 60) return `${minutes}min`;
    if (hours < 24) return `${hours}h`;
    if (days < 7) return `${days}j`;
    return new Date(date).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' });
  };

  const formatMessageTime = (date) => {
    return new Date(date).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
  };

  const formatRecordingTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Créer nouvelle conversation
  const startNewChat = (contact) => {
    const existingChat = chats.find(c => c.name === contact.displayName);
    if (existingChat) {
      setSelectedChat(existingChat);
    } else {
      const newChat = {
        id: Date.now().toString(),
        name: contact.displayName,
        type: 'dm',
        avatar: contact.avatar,
        lastMessage: '',
        lastMessageTime: new Date(),
        unread: 0,
        online: contact.online
      };
      setChats([newChat, ...chats]);
      setSelectedChat(newChat);
    }
    setShowNewChat(false);
  };

  // Filtrer chats par recherche
  const filteredChats = chats.filter(chat =>
    chat.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // VUE AUTHENTIFICATION
  if (currentView === 'auth') {
    return (
      <div className="h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center p-4">
        <div className="bg-white rounded-3xl shadow-2xl w-full max-w-md p-8 backdrop-blur-sm bg-opacity-95">
          <div className="text-center mb-8">
            <div className="text-6xl mb-4 animate-bounce">💬</div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-pink-600 bg-clip-text text-transparent">
              Friamais
            </h1>
            <p className="text-gray-600 mt-2">Messagerie temps réel sécurisée</p>
          </div>

          <div className="space-y-4">
            {authMode === 'signup' && (
              <>
                <input
                  type="text"
                  placeholder="Nom d'utilisateur"
                  value={formData.username}
                  onChange={(e) => setFormData({...formData, username: e.target.value})}
                  className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:outline-none transition"
                />
                <input
                  type="text"
                  placeholder="Nom d'affichage"
                  value={formData.displayName}
                  onChange={(e) => setFormData({...formData, displayName: e.target.value})}
                  className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:outline-none transition"
                />
              </>
            )}
            <input
              type="email"
              placeholder="Email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              onKeyPress={(e) => e.key === 'Enter' && handleAuth()}
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:outline-none transition"
            />
            <input
              type="password"
              placeholder="Mot de passe"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              onKeyPress={(e) => e.key === 'Enter' && handleAuth()}
              className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-500 focus:outline-none transition"
            />
            <button
              onClick={handleAuth}
              className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white py-3 rounded-xl font-semibold hover:shadow-lg transform hover:scale-105 transition"
            >
              {authMode === 'login' ? 'Se connecter' : "S'inscrire"}
            </button>
          </div>

          <div className="mt-6 text-center">
            <button
              onClick={() => setAuthMode(authMode === 'login' ? 'signup' : 'login')}
              className="text-purple-600 hover:text-purple-800 font-medium"
            >
              {authMode === 'login' ? "Pas de compte ? S'inscrire" : 'Déjà un compte ? Se connecter'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  // VUE CHAT
  return (
    <div className="h-screen flex bg-gray-50 relative">
      {/* NOTIFICATIONS */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {notifications.map(notif => (
          <div
            key={notif.id}
            className={`px-4 py-3 rounded-lg shadow-lg flex items-center gap-2 animate-slide-in ${
              notif.type === 'error' ? 'bg-red-500' : 'bg-indigo-500'
            } text-white`}
          >
            <AlertCircle size={18} />
            <span className="text-sm">{notif.message}</span>
          </div>
        ))}
      </div>

      {/* Audio player caché */}
      <audio ref={audioRef} onEnded={() => setPlayingAudio(null)} />

      {/* SIDEBAR */}
      <div className="w-96 bg-white border-r border-gray-200 flex flex-col">
        {/* Header User */}
        <div className="p-4 bg-gradient-to-r from-indigo-500 to-purple-600 text-white">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="text-3xl">{user?.avatar}</div>
                <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-400 rounded-full border-2 border-white"></div>
              </div>
              <div>
                <div className="font-semibold">{user?.displayName}</div>
                <div className="text-xs opacity-90">@{user?.username}</div>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="hover:bg-white/20 p-2 rounded-lg transition"
            >
              <LogOut size={20} />
            </button>
          </div>

          {/* Barre de recherche */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-white/70" size={18} />
            <input
              type="text"
              placeholder="Rechercher..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-lg bg-white/20 text-white placeholder-white/70 focus:bg-white/30 focus:outline-none"
            />
          </div>
        </div>

        {/* Nouvelle conversation */}
        <div className="p-3 border-b">
          <button
            onClick={() => setShowNewChat(!showNewChat)}
            className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white py-2.5 rounded-lg hover:shadow-lg transition"
          >
            <Plus size={20} />
            Nouvelle conversation
          </button>
        </div>

        {/* Panel nouveaux contacts */}
        {showNewChat && (
          <div className="p-4 bg-indigo-50 border-b">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-semibold text-gray-800">Contacts</h3>
              <button onClick={() => setShowNewChat(false)} className="text-gray-500 hover:text-gray-700">
                <X size={18} />
              </button>
            </div>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {contacts.map(contact => (
                <button
                  key={contact.id}
                  onClick={() => startNewChat(contact)}
                  className="w-full flex items-center gap-3 p-2.5 rounded-lg hover:bg-white transition"
                >
                  <div className="relative">
                    <div className="text-2xl">{contact.avatar}</div>
                    {contact.online && (
                      <div className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-green-500 rounded-full border-2 border-white"></div>
                    )}
                  </div>
                  <div className="text-left flex-1">
                    <div className="font-medium text-sm">{contact.displayName}</div>
                    <div className="text-xs text-gray-500">@{contact.username}</div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Liste conversations */}
        <div className="flex-1 overflow-y-auto">
          {filteredChats.map(chat => (
            <button
              key={chat.id}
              onClick={() => setSelectedChat(chat)}
              className={`w-full p-4 flex items-start gap-3 hover:bg-gray-50 transition border-l-4 relative ${
                selectedChat?.id === chat.id 
                  ? 'bg-indigo-50 border-indigo-500' 
                  : 'border-transparent'
              }`}
            >
              {mutedChats.includes(chat.id) && (
                <BellOff size={14} className="absolute top-2 right-2 text-gray-400" />
              )}
              <div className="relative flex-shrink-0">
                <div className="text-3xl">{chat.avatar}</div>
                {chat.type === 'dm' && chat.online && (
                  <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></div>
                )}
              </div>
              <div className="flex-1 text-left min-w-0">
                <div className="flex items-center justify-between mb-1">
                  <div className="font-semibold text-gray-900 truncate flex items-center gap-2">
                    {chat.name}
                    {chat.type === 'group' && (
                      <span className="text-xs text-gray-500">({chat.members})</span>
                    )}
                  </div>
                  <div className="text-xs text-gray-500 flex-shrink-0">
                    {formatTime(chat.lastMessageTime)}
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-600 truncate">{chat.lastMessage}</div>
                  {chat.unread > 0 && (
                    <div className="flex-shrink-0 ml-2 bg-indigo-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center font-medium">
                      {chat.unread}
                    </div>
                  )}
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* ZONE CHAT */}
      <div className="flex-1 flex flex-col">
        {selectedChat ? (
          <>
            {/* Header Chat */}
            <div className="p-4 bg-white border-b shadow-sm flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <div className="text-4xl">{selectedChat.avatar}</div>
                  {selectedChat.type === 'dm' && selectedChat.online && (
                    <div className="absolute bottom-0 right-0 w-3.5 h-3.5 bg-green-500 rounded-full border-2 border-white"></div>
                  )}
                </div>
                <div>
                  <div className="font-semibold text-gray-900 text-lg">{selectedChat.name}</div>
                  <div className="text-sm text-gray-500">
                    {selectedChat.type === 'dm' 
                      ? (selectedChat.online ? '● En ligne' : 'Hors ligne')
                      : `${selectedChat.members} membres`
                    }
                  </div>
                </div>
              </div>
              <div className="flex gap-2">
                <button className="p-2.5 hover:bg-gray-100 rounded-lg transition">
                  <Video size={20} className="text-gray-600" />
                </button>
                <button 
                  onClick={() => toggleMuteChat(selectedChat.id)}
                  className="p-2.5 hover:bg-gray-100 rounded-lg transition"
                >
                  {mutedChats.includes(selectedChat.id) ? (
                    <BellOff size={20} className="text-gray-600" />
                  ) : (
                    <Bell size={20} className="text-gray-600" />
                  )}
                </button>
                <button className="p-2.5 hover:bg-gray-100 rounded-lg transition">
                  <MoreVertical size={20} className="text-gray-600" />
                </button>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gradient-to-b from-gray-50 to-white">
              {messages.map((msg, idx) => {
                const isOwn = msg.senderId === user.id;
                const showAvatar = idx === 0 || messages[idx - 1].senderId !== msg.senderId;
                
                return (
                  <div key={msg.id} className={`flex ${isOwn ? 'justify-end' : 'justify-start'} gap-2`}>
                    {!isOwn && showAvatar && (
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center text-white font-semibold text-sm flex-shrink-0">
                        {selectedChat.avatar}
                      </div>
                    )}
                    {!isOwn && !showAvatar && <div className="w-8"></div>}
                    
                    <div className={`max-w-md ${isOwn ? 'items-end' : 'items-start'} flex flex-col gap-1`}>
                      {/* Message répondu */}
                      {msg.replyTo && (
                        <div className="text-xs bg-gray-100 px-3 py-1.5 rounded-lg border-l-2 border-indigo-500 mb-1">
                          <div className="font-semibold text-gray-700">Réponse à:</div>
                          <div className="text-gray-600 truncate">{msg.replyTo.content}</div>
                        </div>
                      )}
                      
                      <div className="relative group">
                        <div
                          className={`px-4 py-2.5 rounded-2xl ${
                            isOwn
                              ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-br-sm'
                              : 'bg-white border border-gray-200 text-gray-800 rounded-bl-sm shadow-sm'
                          }`}
                        >
                          {msg.type === 'image' ? (
                            <img src={msg.fileUrl} alt="Image" className="rounded-lg max-w-xs cursor-pointer hover:opacity-90 transition" />
                          ) : msg.type === 'file' ? (
                            <div className="flex items-center gap-2">
                              <File size={20} />
                              <span className="text-sm">{msg.content}</span>
                            </div>
                          ) : msg.type === 'audio' ? (
                            <div className="flex items-center gap-3">
                              <button
                                onClick={() => toggleAudioPlay(msg.audioUrl)}
                                className={`p-2 rounded-full ${isOwn ? 'bg-white/20 hover:bg-white/30' : 'bg-indigo-100 hover:bg-indigo-200'} transition`}
                              >
                                {playingAudio === msg.audioUrl ? (
                                  <Pause size={16} className={isOwn ? 'text-white' : 'text-indigo-600'} />
                                ) : (
                                  <Play size={16} className={isOwn ? 'text-white' : 'text-indigo-600'} />
                                )}
                              </button>
                              <div className="flex-1">
                                <div className="h-1 bg-white/30 rounded-full overflow-hidden">
                                  <div className="h-full bg-white/50 w-0"></div>
                                </div>
                                <div className="text-xs mt-1 opacity-75">{msg.duration}s</div>
                              </div>
                            </div>
                          ) : (
                            <>
                              <p className="text-sm leading-relaxed">{msg.content}</p>
                              {msg.edited && (
                                <span className="text-xs opacity-70 italic ml-2">(modifié)</span>
                              )}
                            </>
                          )}
                        </div>
                        
                        {/* Menu contextuel */}
                        <button
                          onClick={() => setSelectedMessage(selectedMessage === msg.id ? null : msg.id)}
                          className={`absolute ${isOwn ? 'left-0 -translate-x-8' : 'right-0 translate-x-8'} top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-200 rounded transition`}
                        >
                          <MoreVertical size={16} />
                        </button>
                        
                        {selectedMessage === msg.id && (
                          <div className={`absolute ${isOwn ? 'right-0' : 'left-0'} top-full mt-2 bg-white rounded-lg shadow-xl border border-gray-200 py-1 z-10 w-48`}>
                            <button
                              onClick={() => handleReplyMessage(msg)}
                              className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 flex items-center gap-2"
                            >
                              <Reply size={16} />
                              Répondre
                            </button>
                            <button
                              onClick={() => handleCopyMessage(msg.content)}
                              className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 flex items-center gap-2"
                            >
                              <Copy size={16} />
                              Copier
                            </button>
                            {isOwn && msg.type === 'text' && (
                              <button
                                onClick={() => handleEditMessage(msg)}
                                className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 flex items-center gap-2"
                              >
                                <Edit2 size={16} />
                                Modifier
                              </button>
                            )}
                            {isOwn && (
                              <button
                                onClick={() => handleDeleteMessage(msg.id)}
                                className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 text-red-600 flex items-center gap-2"
                              >
                                <Trash2 size={16} />
                                Supprimer
                              </button>
                            )}
                          </div>
                        )}
                      </div>
                      
                      {/* Réactions */}
                      {msg.reactions.length > 0 && (
                        <div className="flex gap-1 flex-wrap">
                          {Object.entries(
                            msg.reactions.reduce((acc, r) => {
                              acc[r.emoji] = (acc[r.emoji] || 0) + 1;
                              return acc;
                            }, {})
                          ).map(([emoji, count]) => (
                            <button
                              key={emoji}
                              className="px-2 py-0.5 bg-white border border-gray-300 rounded-full text-xs flex items-center gap-1 hover:border-indigo-500 transition"
                            >
                              <span>{emoji}</span>
                              <span className="text-gray-600">{count}</span>
                            </button>
                          ))}
                        </div>
                      )}
                      
                      {/* Bouton ajouter réaction */}
                      <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition">
                        {reactions.map(reaction => (
                          <button
                            key={reaction.emoji}
                            onClick={() => addReaction(msg.id, reaction.emoji)}
                            className="w-7 h-7 hover:bg-gray-200 rounded-full flex items-center justify-center transition text-base"
                            title={reaction.label}
                          >
                            {reaction.emoji}
                          </button>
                        ))}
                      </div>
                      
                      <div className={`flex items-center gap-1 text-xs text-gray-500 px-1`}>
                        <span>{formatMessageTime(msg.timestamp)}</span>
                        {isOwn && (
                          msg.status === 'read' ? <CheckCheck size={14} className="text-blue-500" /> :
                          msg.status === 'delivered' ? <CheckCheck size={14} /> :
                          <Check size={14} />
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
              <div ref={messagesEndRef} />
            </div>

            {/* Zone réponse */}
            {replyingTo && (
              <div className="px-4 py-2 bg-indigo-50 border-t flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Reply size={16} className="text-indigo-600" />
                  <div className="text-sm">
                    <div className="font-semibold text-gray-700">Réponse à {replyingTo.senderId === user.id ? 'vous-même' : selectedChat.name}</div>
                    <div className="text-gray-600 truncate max-w-md">{replyingTo.content}</div>
                  </div>
                </div>
                <button onClick={() => setReplyingTo(null)} className="p-1 hover:bg-white rounded">
                  <X size={16} />
                </button>
              </div>
            )}

            {/* Zone édition */}
            {editingMessage && (
              <div className="px-4 py-2 bg-yellow-50 border-t flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Edit2 size={16} className="text-yellow-600" />
                  <div className="text-sm font-semibold text-gray-700">Modification du message</div>
                </div>
                <button onClick={() => { setEditingMessage(null); setMessageInput(''); }} className="p-1 hover:bg-white rounded">
                  <X size={16} />
                </button>
              </div>
            )}

            {/* Preview audio enregistré */}
            {audioBlob && (
              <div className="px-4 py-3 bg-green-50 border-t flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Mic size={20} className="text-green-600" />
                  <div className="text-sm">
                    <div className="font-semibold text-gray-700">Message vocal prêt</div>
                    <div className="text-gray-600">{formatRecordingTime(recordingTime)}</div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button onClick={cancelRecording} className="px-3 py-1 text-sm text-red-600 hover:bg-red-100 rounded transition">
                    Annuler
                  </button>
                  <button onClick={handleSendMessage} className="px-3 py-1 text-sm bg-green-600 text-white hover:bg-green-700 rounded transition">
                    Envoyer
                  </button>
                </div>
              </div>
            )}

            {/* Input */}
            <div className="p-4 bg-white border-t shadow-lg">
              {isRecording ? (
                <div className="flex items-center gap-3">
                  <div className="flex-1 flex items-center gap-3 bg-red-50 px-4 py-3 rounded-xl border-2 border-red-200">
                    <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                    <span className="font-mono text-lg text-red-600">{formatRecordingTime(recordingTime)}</span>
                    <span className="text-gray-600">Enregistrement en cours...</span>
                  </div>
                  <button
                    onClick={cancelRecording}
                    className="p-3 hover:bg-gray-100 rounded-xl transition"
                  >
                    <X size={22} className="text-gray-600" />
                  </button>
                  <button
                    onClick={stopRecording}
                    className="p-3 bg-red-500 text-white rounded-xl hover:bg-red-600 transition"
                  >
                    <StopCircle size={22} />
                  </button>
                </div>
              ) : (
                <div className="flex items-end gap-2">
                  <input
                    ref={fileInputRef}
                    type="file"
                    onChange={(e) => handleFileUpload(e, 'file')}
                    className="hidden"
                    accept="application/pdf,.doc,.docx,.txt"
                  />
                  <input
                    ref={imageInputRef}
                    type="file"
                    onChange={(e) => handleFileUpload(e, 'image')}
                    className="hidden"
                    accept="image/*"
                  />
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="p-3 hover:bg-gray-100 rounded-xl transition flex-shrink-0"
                  >
                    <Paperclip size={22} className="text-gray-600" />
                  </button>
                  <button
                    onClick={() => imageInputRef.current?.click()}
                    className="p-3 hover:bg-gray-100 rounded-xl transition flex-shrink-0"
                  >
                    <ImageIcon size={22} className="text-gray-600" />
                  </button>
                  <button
                    onClick={startRecording}
                    className="p-3 hover:bg-gray-100 rounded-xl transition flex-shrink-0"
                  >
                    <Mic size={22} className="text-gray-600" />
                  </button>
                  <div className="flex-1 relative">
                    <textarea
                      value={messageInput}
                      onChange={(e) => setMessageInput(e.target.value)}
                      onKeyPress={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault();
                          handleSendMessage();
                        }
                      }}
                      placeholder={editingMessage ? "Modifiez votre message..." : "Écrivez votre message..."}
                      rows="1"
                      className="w-full px-4 py-3 pr-12 rounded-xl border-2 border-gray-200 focus:border-indigo-500 focus:outline-none resize-none"
                      style={{ minHeight: '48px', maxHeight: '120px' }}
                    />
                    <button 
                      onClick={() => setShowEmojiPicker(!showEmojiPicker)}
                      className="absolute right-3 bottom-3 hover:bg-gray-100 p-1.5 rounded-lg transition"
                    >
                      <Smile size={20} className="text-gray-500" />
                    </button>
                    
                    {/* Emoji picker */}
                    {showEmojiPicker && (
                      <div className="absolute bottom-full right-0 mb-2 bg-white rounded-xl shadow-xl border border-gray-200 p-3">
                        <div className="grid grid-cols-6 gap-2">
                          {emojis.map(emoji => (
                            <button
                              key={emoji}
                              onClick={() => {
                                setMessageInput(messageInput + emoji);
                                setShowEmojiPicker(false);
                              }}
                              className="text-2xl hover:bg-gray-100 rounded p-2 transition"
                            >
                              {emoji}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                  <button
                    onClick={handleSendMessage}
                    disabled={!messageInput.trim() && !audioBlob}
                    className={`p-3 rounded-xl transition flex-shrink-0 ${
                      messageInput.trim() || audioBlob
                        ? 'bg-gradient-to-r from-indigo-500 to-purple-600 text-white hover:shadow-lg transform hover:scale-105'
                        : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    }`}
                  >
                    <Send size={22} />
                  </button>
                </div>
              )}
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center bg-gradient-to-br from-gray-50 to-white">
            <div className="text-center">
              <div className="text-6xl mb-4 opacity-50">💬</div>
              <p className="text-xl text-gray-400 font-medium">Sélectionnez une conversation</p>
              <p className="text-sm text-gray-400 mt-2">Choisissez un contact pour commencer à discuter</p>
            </div>
          </div>
        )}
      </div>

      <style>{`
        @keyframes slide-in {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
        .animate-slide-in {
          animation: slide-in 0.3s ease-out;
        }
      `}</style>
    </div>
  );
};

export default Friamais;<Phone size={20} className="text-gray-600" />
                </button>
                <button className="p-2.5 hover:bg-gray-100 rounded-lg transition">
