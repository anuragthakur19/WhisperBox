const socket = io();
const room = ROOM_ID_FROM_TEMPLATE; // Replace with actual room ID passed from Flask via template
let username = "";

// Emit join event
socket.emit('join', { room });

// Set user name when server sends it
socket.on('self_name', data => {
  username = data.name;
  showPopup(`${username} joined the chat`);
});

// Show join popup
socket.on('user_joined', data => {
  showPopup(`${data.name} joined`);
});

// Show leave notification
socket.on('user_left', data => {
  showPopup(`${data.name} left`);
});

// Render messages
socket.on('message', data => {
  appendMessage(`<strong>${data.name}</strong>: ${data.text}`);
});

// File shared link
socket.on('file_shared', data => {
  appendMessage(
    `<strong>${data.name}</strong> shared: <a href="${data.url}" target="_blank" class="text-blue-400 underline">${data.filename}</a>`
  );
});

// Room deleted
socket.on('room_deleted', () => {
  alert("Room was deleted due to inactivity.");
  window.location.href = "/";
});

// Message submit
document.getElementById('message-form').onsubmit = e => {
  e.preventDefault();
  const input = document.getElementById('message-input');
  if (input.value.trim()) {
    socket.emit('send_message', { room, msg: input.value });
    input.value = '';
  }
};

// File input
document.getElementById('file-input').addEventListener('change', function () {
  const file = this.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('file', file);

  fetch(`https://transfer.sh/${file.name}`, {
    method: 'POST',
    body: formData
  })
    .then(res => res.text())
    .then(url => {
      socket.emit('send_file', {
        room,
        filename: file.name,
        url: url
      });
    })
    .catch(err => {
      alert("Upload failed.");
      console.error(err);
    });
});

// Optional: Typing Indicator
let typing = false;
let typingTimeout;

document.getElementById('message-input').addEventListener('input', () => {
  if (!typing) {
    typing = true;
    socket.emit('typing', { room, name: username });
    typingTimeout = setTimeout(stopTyping, 2000);
  } else {
    clearTimeout(typingTimeout);
    typingTimeout = setTimeout(stopTyping, 2000);
  }
});

socket.on('user_typing', data => {
  showTyping(data.name);
});

function stopTyping() {
  typing = false;
  document.getElementById('typing-indicator').innerText = '';
}

function showTyping(name) {
  document.getElementById('typing-indicator').innerText = `${name} is typing...`;
}

// Helpers
function appendMessage(html) {
  const el = document.createElement('div');
  el.innerHTML = html;
  document.getElementById('messages').appendChild(el);
  document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
}

function showPopup(msg) {
  const popup = document.createElement('div');
  popup.className = "fixed top-4 right-4 bg-blue-700 text-white px-4 py-2 rounded shadow-lg z-50 animate-bounce";
  popup.innerText = msg;
  document.body.appendChild(popup);
  setTimeout(() => popup.remove(), 3000);
}
