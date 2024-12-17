document.addEventListener('DOMContentLoaded', (event) => {
    const socket = io();
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const output = document.getElementById('output');
    recordingIndicator = document.getElementById('recordingIndicator');
    let isRecording = false;

    startBtn.disabled = false;
    stopBtn.disabled = true;
    
    recordingIndicator.classList.add('hidden');

    document.addEventListener('click', (event) => {
        console.log('Elemento clickeado:', event.target);
    });
    
    socket.on('recognition_result', (data) => {
        switch(data.status) {
            case 'confirm':
                // Crear contenedor para el mensaje y el botón
                const container = document.createElement('div');
                container.classList.add('mb-4', 'p-2', 'rounded-lg', 'bg-blue-100');
                
                // Agregar el texto reconocido
                const textElement = document.createElement('p');
                textElement.textContent = `Texto reconocido: "${data.text}"`;
                textElement.classList.add('mb-2', 'font-medium');
                
                // Agregar la información de la placa
                const plateElement = document.createElement('p');
                plateElement.textContent = `Esta es su placa: ${data.placa}?`;
                plateElement.classList.add('mb-2', 'font-bold');
                
                // Crear botón de confirmación
                // const confirmBtn = document.createElement('button');
                // confirmBtn.textContent = 'Confirmar Placa';
                // confirmBtn.classList.add(
                //     'bg-green-500', 'text-white', 'px-4', 'py-2', 'rounded',
                //     'hover:bg-green-600', 'transition-colors'
                // );
                
                // Agregar evento al botón
                // confirmBtn.onclick = () => {
                //     socket.emit('confirm_plate', {
                //         plate: data.plate,
                //         type: data.type
                //     });
                //     confirmBtn.disabled = true;
                //     confirmBtn.classList.add('opacity-50');
                // };
                
                // Agregar elementos al contenedor
                container.appendChild(textElement);
                container.appendChild(plateElement);
                // container.appendChild(confirmBtn);
                
                // Agregar contenedor al output
                output.appendChild(container);
                output.scrollTop = output.scrollHeight;
                break;

            case 'success':
                addMessage(data.text, 'success');
                break;

            case 'error':
                addMessage(data.text, 'error');
                break;

            case 'exit':
                addMessage('Reconocimiento finalizado por comando de voz', 'info');
                stopBtn.click();
                break;
            case 'info':
                // Mostrar la información de la placa en la interfaz
                // addMessage(`Texto reconocido: ${data.text}`, 'info');
                console.log("data.placa es igual a: ",data)
                if ((data.plate == null) || (data.plate == undefined)) {
                    addMessage(`Vuelva a repetir la placa, por favor`, 'info');
                    break;
                }
                else{
                    addMessage(`¿Esta es su placa: ${data.plate} ?`, 'info');
                    return true;
                }
                
        }
    });

    startBtn.addEventListener('click', () => {
        if (!isRecording) {
            socket.emit('start_recognition');
            startBtn.disabled = true;
            stopBtn.disabled = false;
            recordingIndicator.classList.remove('hidden');
            //addMessage('Iniciando reconocimiento...', 'info');
            isRecording = true;
        }
    });

    stopBtn.addEventListener('click', () => {
        if (isRecording) {
            socket.emit('prueba')
            socket.emit('stop_recognition');
            startBtn.disabled = false;
            stopBtn.disabled = true;
            recordingIndicator.classList.add('hidden');
            //addMessage('Reconocimiento detenido', 'warning');
            isRecording = false;
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
        messageElement.classList.add('message', 'font-serif', 'mb-4', 'p-2', 'rounded-lg'); // Aplicar la tipografía Times New Roman y fondo redondeado

        switch(type) {
            case 'spoken':
            messageElement.classList.add('bg-gray-100', 'text-black', 'font-medium');
            break;
        case 'plate':  // Nuevo caso para las placas válidas
            messageElement.classList.add('bg-green-100', 'text-green-800', 'font-bold', 'text-center');
            break;
        case 'error':
            messageElement.classList.add('bg-red-100', 'text-red-500', 'font-medium');
            break;
        case 'warning':
            messageElement.classList.add('bg-yellow-100', 'text-yellow-500', 'font-medium', 'text-center');
            break;
        case 'info':
            messageElement.classList.add('bg-blue-100', 'text-blue-500', 'font-medium', 'text-center');
            break;
        case 'waiting':
            messageElement.classList.add('bg-purple-100', 'text-purple-500', 'font-medium');
            break;
        }
        
        //agregar el mensaje al contenido de salida y asegurar que siempre esta visible el mensaje mas reciente
        output.appendChild(messageElement);
        output.scrollTop = output.scrollHeight;

        return messageElement;//devuelve el elemento para interactuar con el en otras funciones
    }

    /* Actualiza el texto del mensaje en intervalos de 1 segundo y, cuando termina la cuenta regresiva, cambia el texto a "Puede hablar ahora". */
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