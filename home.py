import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, Send, Paperclip, LogOut, Search, Plus, X, Phone, Video, MoreVertical, Smile, Check, CheckCheck, Mic, StopCircle, Play, Pause, AlertCircle, Trash2, Edit2, Reply, Copy, Bell, BellOff, Image as ImageIcon, File } from 'lucide-react';
import { createClient } from '@supabase/supabase-js';

// Configuration Supabase - À remplacer par vos vraies clés
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://qeapxsbygwnwskpppzmz.supabase.co';
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFlYXB4c2J5Z3dud3NrcHBwem16Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjIwMTgwNjMsImV4cCI6MjA3NzU5NDA2M30.35iZdJrMpbQxeTsO2BdE8ndZ5SQ411le50wGMR7sBd0';
const supabase = createClient(supabaseUrl, supabaseAnonKey);

const Friamis = () => {
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
  
  // Données réelles depuis Supabase
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

  // Charger les conversations de l'utilisateur
  const loadUserConversations = async () => {
    if (!user) return;
    
    try {
      const { data, error } = await supabase
        .rpc('get_user_conversations', { user_id_param: user.id });
      
      if (error) throw error;
      setChats(data || []);
    } catch (error) {
      console.error('Erreur chargement conversations:', error);
      addNotification('Erreur lors du chargement des conversations', 'error');
    }
  };

  // Charger les contacts
  const loadContacts = async () => {
    if (!user) return;
    
    try {
      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .neq('id', user.id);
      
      if (error) throw error;
      setContacts(data || []);
    } catch (error) {
      console.error('Erreur chargement contacts:', error);
    }
  };

  // Charger les messages d'une conversation
  const loadMessages = async (conversationId) => {
    try {
      const { data, error } = await supabase
        .from('messages')
        .select(`
          *,
          sender:profiles!sender_id(username, display_name, avatar_url),
          reactions(emoji, user_id)
        `)
        .eq('conversation_id', conversationId)
        .order('created_at', { ascending: true });
      
      if (error) throw error;
      setMessages(data || []);
    } catch (error) {
      console.error('Erreur chargement messages:', error);
      addNotification('Erreur lors du chargement des messages', 'error');
    }
  };

  // S'abonner aux nouveaux messages en temps réel
  useEffect(() => {
    if (!selectedChat) return;

    const channel = supabase
      .channel('messages')
      .on(
        'postgres_changes',
        {
          event: 'INSERT',
          schema: 'public',
          table: 'messages',
          filter: `conversation_id=eq.${selectedChat.id}`
        },
        (payload) => {
          setMessages(prev => [...prev, payload.new]);
          if (payload.new.sender_id !== user.id) {
            addNotification('Nouveau message reçu');
          }
        }
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
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
      const { data: { session } } = await supabase.auth.getSession();
      if (session) {
        const { data: profile } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', session.user.id)
          .single();
        
        setUser({
          id: session.user.id,
          email: session.user.email,
          ...profile
        });
        setCurrentView('chat');
      }
    };
    checkSession();
  }, []);

  // Charger données quand user connecté
  useEffect(() => {
    if (user) {
      loadUserConversations();
      loadContacts();
    }
  }, [user]);

  // Charger messages quand chat sélectionné
  useEffect(() => {
    if (selectedChat) {
      loadMessages(selectedChat.id);
    }
  }, [selectedChat]);

  // Gestion authentification
  const handleAuth = async () => {
    const { email, password, username, displayName } = formData;
    
    if (!email || !password) {
      addNotification('Email et mot de passe requis', 'error');
      return;
    }
    if (authMode === 'signup' && (!username || !displayName)) {
      addNotification('Tous les champs sont requis', 'error');
      return;
    }

    try {
      let result;
      if (authMode === 'signup') {
        result = await supabase.auth.signUp({
          email,
          password,
          options: {
            data: {
              username,
              display_name: displayName
            }
          }
        });
      } else {
        result = await supabase.auth.signInWithPassword({ email, password });
      }

      if (result.error) throw result.error;

      const { data: profile } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', result.data.user.id)
        .single();

      setUser({
        id: result.data.user.id,
        email,
        ...profile
      });
      setCurrentView('chat');
      addNotification('Connexion réussie !');
    } catch (error) {
      console.error('Auth error:', error);
      addNotification(error.message, 'error');
    }
  };

  // Déconnexion
  const handleLogout = async () => {
    await supabase.auth.signOut();
    setUser(null);
    setCurrentView('auth');
    setSelectedChat(null);
    setMessages([]);
    setChats([]);
  };

  // Envoyer un message
  const handleSendMessage = async () => {
    if ((!messageInput.trim() && !audioBlob) || !selectedChat) return;

    try {
      let messageData = {
        conversation_id: selectedChat.id,
        sender_id: user.id,
        content: messageInput,
        content_type: 'text',
        reply_to: replyingTo?.id || null
      };

      if (audioBlob) {
        // Upload audio vers Supabase Storage
        const fileName = `${user.id}/${Date.now()}.webm`;
        const { data: uploadData, error: uploadError } = await supabase.storage
          .from('attachments')
          .upload(fileName, audioBlob);

        if (uploadError) throw uploadError;

        const { data: { publicUrl } } = supabase.storage
          .from('attachments')
          .getPublicUrl(fileName);

        messageData = {
          ...messageData,
          content: `Message vocal (${recordingTime}s)`,
          content_type: 'audio',
          file_url: publicUrl
        };
        setAudioBlob(null);
      }

      if (editingMessage) {
        const { error } = await supabase
          .from('messages')
          .update({ content: messageInput, edited: true })
          .eq('id', editingMessage.id);

        if (error) throw error;
        setEditingMessage(null);
        await loadMessages(selectedChat.id);
      } else {
        const { error } = await supabase
          .from('messages')
          .insert([messageData]);

        if (error) throw error;
      }

      setMessageInput('');
      setReplyingTo(null);
    } catch (error) {
      console.error('Erreur envoi message:', error);
      addNotification('Erreur lors de l\'envoi du message', 'error');
    }
  };

  // Upload fichier
  const handleFileUpload = async (e, type = 'file') => {
    const file = e.target.files?.[0];
    if (!file || !selectedChat) return;

    try {
      const fileName = `${user.id}/${Date.now()}_${file.name}`;
      const { data, error } = await supabase.storage
        .from('attachments')
        .upload(fileName, file);

      if (error) throw error;

      const { data: { publicUrl } } = supabase.storage
        .from('attachments')
        .getPublicUrl(fileName);

      await supabase.from('messages').insert([{
        conversation_id: selectedChat.id,
        sender_id: user.id,
        content: file.name,
        content_type: type === 'image' ? 'image' : 'file',
        file_url: publicUrl
      }]);

      addNotification('Fichier envoyé avec succès');
    } catch (error) {
      console.error('Erreur upload fichier:', error);
      addNotification('Erreur lors de l\'envoi du fichier', 'error');
    }
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
  const addReaction = async (messageId, emoji) => {
    try {
      const { error } = await supabase
        .from('reactions')
        .upsert({
          message_id: messageId,
          user_id: user.id,
          emoji
        });

      if (error) throw error;
      await loadMessages(selectedChat.id);
      setSelectedMessage(null);
    } catch (error) {
      console.error('Erreur ajout réaction:', error);
    }
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

  const handleDeleteMessage = async (messageId) => {
    try {
      const { error } = await supabase
        .from('messages')
        .delete()
        .eq('id', messageId);

      if (error) throw error;
      await loadMessages(selectedChat.id);
      setSelectedMessage(null);
      addNotification('Message supprimé');
    } catch (error) {
      console.error('Erreur suppression:', error);
      addNotification('Erreur lors de la suppression', 'error');
    }
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
  const startNewChat = async (contact) => {
    try {
      // Vérifier si conversation existe déjà
      const existingChat = chats.find(c => 
        c.kind === 'dm' && c.name === contact.display_name
      );
      
      if (existingChat) {
        setSelectedChat(existingChat);
        setShowNewChat(false);
        return;
      }

      // Créer nouvelle conversation
      const { data: convData, error: convError } = await supabase
        .from('conversations')
        .insert([{
          kind: 'dm',
          name: contact.display_name,
          avatar_url: contact.avatar_url,
          created_by: user.id
        }])
        .select()
        .single();

      if (convError) throw convError;

      // Ajouter les membres
      const { error: membersError } = await supabase
        .from('conversation_members')
        .insert([
          { conversation_id: convData.id, user_id: user.id },
          { conversation_id: convData.id, user_id: contact.id }
        ]);

      if (membersError) throw membersError;

      await loadUserConversations();
      setSelectedChat(convData);
      setShowNewChat(false);
      addNotification('Conversation créée');
    } catch (error) {
      console.error('Erreur création conversation:', error);
      addNotification('Erreur lors de la création', 'error');
    }
  };

  // Filtrer chats par recherche
  const filteredChats = chats.filter(chat =>
    chat.name?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // VUE AUTHENTIFICATION
  if (currentView === 'auth') {
    return (
      <div className="h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center p-4">
        <div className="bg-white rounded-3xl shadow-2xl w-full max-w-md p-8 backdrop-blur-sm bg-opacity-95">
          <div className="text-center mb-8">
            <div className="text-6xl mb-4 animate-bounce">💬</div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-pink-600 bg-clip-text text-transparent">
              Friamis 
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
                <div className="text-3xl">{user?.avatar_url || '😊'}</div>
                <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-400 rounded-full border-2 border-white"></div>
              </div>
              <div>
                <div className="font-semibold">{user?.display_name}</div>
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
              {contacts.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-4">Aucun contact disponible</p>
              ) : (
                contacts.map(contact => (
                  <button
                    key={contact.id}
                    onClick={() => startNewChat(contact)}
                    className="w-full flex items-center gap-3 p-2.5 rounded-lg hover:bg-white transition"
                  >
                    <div className="text-2xl">{contact.avatar_url || '👤'}</div>
                    <div className="text-left flex-1">
                      <div className="font-medium text-sm">{contact.display_name}</div>
                      <div className="text-xs text-gray-500">@{contact.username}</div>
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>
        )}

        {/* Liste conversations */}
        <div className="flex-1 overflow-y-auto">
          {filteredChats.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-400">
              <MessageCircle size={48} className="mb-2 opacity-50" />
              <p className="text-sm">Aucune conversation</p>
            </div>
          ) : (
            filteredChats.map(chat => (
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
                <div className="text-3xl flex-shrink-0">{chat.avatar_url || '💬'}</div>
                <div className="flex-1 text-left min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <div className="font-semibold text-gray-900 truncate">
                      {chat.name || 'Conversation'}
                    </div>
                    <div className="text-xs text-gray-500 flex-shrink-0">
                      {formatTime(chat.last_message_time)}
                    </div>
                  </div>
                  <div className="text-sm text-gray-600 truncate">
                    {chat.last_message || 'Aucun message'}
                  </div>
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      {/* ZONE CHAT */}
      <div className="flex-1 flex flex-col">
        {selectedChat ? (
          <>
            {/* Header Chat */}
            <div className="p-4 bg-white border-b shadow-sm flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="text-4xl">{selectedChat.avatar_url || '💬'}</div>
                <div>
                  <div className="font-semibold text-gray-900 text-lg">{selectedChat.name}</div>
                  <div className="text-sm text-gray-500">
                    {selectedChat.kind === 'dm' ? 'Conversation privée' : 'Groupe'}
                  </div>
                </div>
              </div>
              <div className="flex gap-2">
                <button className="p-2.5 hover:bg-gray-100 rounded-lg transition">
                  <Phone size={20} className="text-gray-600" />
                </button>
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
              {messages.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-gray-400">
                  <MessageCircle size={48} className="mb-2 opacity-50" />
                  <p className="text-sm">Aucun message</p>
                  <p className="text-xs mt-1">Envoyez le premier message !</p>
                </div>
              ) : (
                messages.map((msg, idx) => {
                  const isOwn = msg.sender_id === user.id;
                  const showAvatar = idx === 0 || messages[idx - 1].sender_id !== msg.sender_id;
                  
                  return (
                    <div key={msg.id} className={`flex ${isOwn ? 'justify-end' : 'justify-start'} gap-2`}>
                      {!isOwn && showAvatar && (
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center text-white font-semibold text-sm flex-shrink-0">
                          {msg.sender?.avatar_url || '👤'}
                        </div>
                      )}
                      {!isOwn && !showAvatar && <div className="w-8"></div>}
                      
                      <div className={`max-w-md ${isOwn ? 'items-end' : 'items-start'} flex flex-col gap-1`}>
                        {/* Message répondu */}
                        {msg.reply_to && (
                          <div className="text-xs bg-gray-100 px-3 py-1.5 rounded-lg border-l-2 border-indigo-500 mb-1">
                            <div className="font-semibold text-gray-700">Réponse à un message</div>
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
                            {msg.content_type === 'image' ? (
                              <img src={msg.file_url} alt="Image" className="rounded-lg max-w-xs cursor-pointer hover:opacity-90 transition" />
                            ) : msg.content_type === 'file' ? (
                              <div className="flex items-center gap-2">
                                <File size={20} />
                                <span className="text-sm">{msg.content}</span>
                              </div>
                            ) : msg.content_type === 'audio' ? (
                              <div className="flex items-center gap-3">
                                <button
                                  onClick={() => toggleAudioPlay(msg.file_url)}
                                  className={`p-2 rounded-full ${isOwn ? 'bg-white/20 hover:bg-white/30' : 'bg-indigo-100 hover:bg-indigo-200'} transition`}
                                >
                                  {playingAudio === msg.file_url ? (
                                    <Pause size={16} className={isOwn ? 'text-white' : 'text-indigo-600'} />
                                  ) : (
                                    <Play size={16} className={isOwn ? 'text-white' : 'text-indigo-600'} />
                                  )}
                                </button>
                                <div className="flex-1">
                                  <div className="h-1 bg-white/30 rounded-full overflow-hidden">
                                    <div className="h-full bg-white/50 w-0"></div>
                                  </div>
                                  <div className="text-xs mt-1 opacity-75">Audio</div>
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
                              {isOwn && msg.content_type === 'text' && (
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
                        {msg.reactions && msg.reactions.length > 0 && (
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
                          <span>{formatMessageTime(msg.created_at)}</span>
                          {isOwn && <Check size={14} />}
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Zone réponse */}
            {replyingTo && (
              <div className="px-4 py-2 bg-indigo-50 border-t flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Reply size={16} className="text-indigo-600" />
                  <div className="text-sm">
                    <div className="font-semibold text-gray-700">Réponse à un message</div>
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

export default Friamis;
