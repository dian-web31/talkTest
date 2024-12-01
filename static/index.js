document.addEventListener('DOMContentLoaded', (event) => {
    const socket = io();
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const output = document.getElementById('output');
    const recordingIndicator = document.getElementById('recordingIndicator');
    let isRecording = false;

       // Asegúrate de que los botones y el indicador de grabación estén en el estado correcto al cargar la página
       startBtn.disabled = false;
       stopBtn.disabled = true;
       recordingIndicator.classList.add('hidden');

    startBtn.addEventListener('click', () => {
        if (!isRecording) {
            socket.emit('start_recognition');
            startBtn.disabled = true;
            stopBtn.disabled = false;
            recordingIndicator.classList.remove('hidden');
            addMessage('Iniciando reconocimiento...', 'info');
            isRecording = true;
        }
    });

    stopBtn.addEventListener('click', () => {
        if (isRecording) {
            socket.emit('stop_recognition');
            startBtn.disabled = false;
            stopBtn.disabled = true;
            recordingIndicator.classList.add('hidden');
            //addMessage('Reconocimiento detenido', 'warning');
            isRecording = false;
        }
    });

    socket.on('recognition_result', (data) => {
        switch(data.status) {
            case 'success':
                addMessage(data.text, 'spoken');
                break;
            case 'error':
                addMessage(`Error: ${data.text}`, 'error');
                break;
            case 'exit':
                addMessage('Reconocimiento finalizado por comando de voz', 'info');
                stopBtn.click();
                break;
        }
    });

    socket.on('waiting', (data) => {
        const messageElement = addMessage(data.message, 'waiting');
        startCountdown(3, messageElement);
    });

    socket.on('recognition_started', () => {
        addMessage('Reconocimiento de voz iniciado. Puede hablar.', 'info');
    });

    socket.on('recognition_stopped', () => {
        addMessage('Reconocimiento de voz detenido.', 'warning');
        isRecording = false;
    });

    function addMessage(text, type) {
        const messageElement = document.createElement('p');
        messageElement.textContent = text;
        messageElement.classList.add('message','font-serif','mb-4'); // Aplicar la tipografía Times New Roman

        switch(type) {
            case 'spoken':
                messageElement.classList.add('message-spoken', 'font-medium'); // Negro para texto hablado
                break;
            case 'success':
                messageElement.classList.add('text-green-500', 'font-medium', 'text-center');
                break;
            case 'error':
                messageElement.classList.add('text-red-500', 'font-medium');
                break;
            case 'warning':
                messageElement.classList.add('text-yellow-500', 'font-medium', 'text-center');
                break;
            case 'info':
                messageElement.classList.add('text-blue-500', 'font-medium', 'text-center');
                break;
            case 'waiting':
                messageElement.classList.add('text-purple-500', 'font-medium');
                break;
        }
        
        output.appendChild(messageElement);
        output.scrollTop = output.scrollHeight;

        return messageElement;
    }

    function startCountdown(seconds, messageElement) {
        let remainingSeconds = seconds;
        const interval = setInterval(() => {
            if (remainingSeconds > 0) {
                messageElement.textContent = `Esperando ${remainingSeconds} segundos...`;
                remainingSeconds--;
            } else {
                clearInterval(interval);
                messageElement.textContent = 'Puede hablar ahora.';
                messageElement.classList.remove('text-purple-500');
                messageElement.classList.add('text-green-500');
            }
        }, 1000);
    }
});