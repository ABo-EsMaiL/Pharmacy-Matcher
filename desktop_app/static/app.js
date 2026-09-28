let currentProcessId = null;
let selectedWarehouseFiles = [];
let selectedShortageFiles = [];
let serverStatusInterval = null;

// Ensure Pywebview API is ready
window.addEventListener('pywebviewready', function() {
    loadSettings();
    updateServerStatus();
    serverStatusInterval = setInterval(updateServerStatus, 5000);
});

// UI Navigation
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(el => el.classList.remove('active'));
    document.getElementById(screenId).classList.add('active');
    
    // Reset New Process screen if navigating away and back
    if (screenId === 'screen-new') {
        resetNewProcessForm();
    }
}

// Toast Notifications
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : '⚠️';
    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Exit App
async function exitApp() {
    try {
        if (window.pywebview && window.pywebview.api) {
            await window.pywebview.api.on_closing();
        }
    } catch (e) {
        console.error(e);
    }
}

// --- New Process Logic ---
function resetNewProcessForm() {
    selectedWarehouseFiles = [];
    selectedShortageFiles = [];
    updateFileList('warehouse', selectedWarehouseFiles);
    updateFileList('shortage', selectedShortageFiles);
    document.getElementById('progress-area').classList.add('hidden');
    document.getElementById('btn-submit').classList.remove('hidden');
    checkSubmitState();
}

async function selectFiles(type) {
    try {
        const filePaths = await window.pywebview.api.select_files(type);
        if (filePaths && filePaths.length > 0) {
            if (type === 'warehouse') {
                selectedWarehouseFiles = [...selectedWarehouseFiles, ...filePaths];
                updateFileList('warehouse', selectedWarehouseFiles);
            } else if (type === 'shortage') {
                selectedShortageFiles = [...selectedShortageFiles, ...filePaths];
                updateFileList('shortage', selectedShortageFiles);
            }
            checkSubmitState();
        }
    } catch (error) {
        showToast('حدث خطأ أثناء اختيار الملفات', 'error');
        console.error(error);
    }
}

function updateFileList(type, files) {
    const listEl = document.getElementById(`list-${type}`);
    listEl.innerHTML = '';
    files.forEach((path, index) => {
        const fileName = path.split('\\').pop().split('/').pop();
        const li = document.createElement('li');
        li.className = 'file-item';
        li.innerHTML = `
            <span title="${path}">${fileName}</span>
            <button class="btn-remove-file" onclick="removeFile('${type}', ${index})">✕</button>
        `;
        listEl.appendChild(li);
    });
}

function removeFile(type, index) {
    if (type === 'warehouse') {
        selectedWarehouseFiles.splice(index, 1);
        updateFileList('warehouse', selectedWarehouseFiles);
    } else {
        selectedShortageFiles.splice(index, 1);
        updateFileList('shortage', selectedShortageFiles);
    }
    checkSubmitState();
}

function checkSubmitState() {
    const btn = document.getElementById('btn-submit');
    if (selectedWarehouseFiles.length > 0 && selectedShortageFiles.length > 0) {
        btn.removeAttribute('disabled');
    } else {
        btn.setAttribute('disabled', 'true');
    }
}

async function submitProcess() {
    const btn = document.getElementById('btn-submit');
    const progressArea = document.getElementById('progress-area');
    
    btn.classList.add('hidden');
    progressArea.classList.remove('hidden');
    
    try {
        const result = await window.pywebview.api.start_process(
            selectedWarehouseFiles,
            selectedShortageFiles
        );
        
        if (result && result.processId) {
            currentProcessId = result.processId;
            showToast('تمت المطابقة بنجاح!', 'success');
            loadResults(result.stats);
            showScreen('screen-results');
        } else {
            throw new Error('لم يتم إرجاع معرف العملية');
        }
    } catch (error) {
        showToast('حدث خطأ أثناء المطابقة: ' + error, 'error');
        console.error(error);
        btn.classList.remove('hidden');
        progressArea.classList.add('hidden');
    }
}

// --- Results Logic ---
function loadResults(stats) {
    if (!stats) return;
    const total = stats.total ?? stats.total_shortages ?? 0;
    const matched = stats.matched ?? stats.matched_count ?? 0;
    const notfound = stats.not_found ?? stats.not_found_count ?? 0;
    const review = stats.review ?? stats.review_count ?? 0;
    
    document.getElementById('stat-total').innerText = total;
    document.getElementById('stat-matched').innerText = matched;
    document.getElementById('stat-notfound').innerText = notfound;
    document.getElementById('stat-review').innerText = review;
    
    if (total > 0) {
        document.getElementById('stat-matched-pct').innerText = Math.round((matched/total)*100) + '%';
        document.getElementById('stat-notfound-pct').innerText = Math.round((notfound/total)*100) + '%';
        document.getElementById('stat-review-pct').innerText = Math.round((review/total)*100) + '%';
    } else {
        document.getElementById('stat-matched-pct').innerText = '0%';
        document.getElementById('stat-notfound-pct').innerText = '0%';
        document.getElementById('stat-review-pct').innerText = '0%';
    }
}

async function openExcel() {
    if (!currentProcessId) return;
    try {
        await window.pywebview.api.open_excel(currentProcessId);
    } catch (error) {
        showToast('تعذر فتح الملف: ' + error, 'error');
    }
}

async function openFolder() {
    if (!currentProcessId) return;
    try {
        await window.pywebview.api.open_folder(currentProcessId);
    } catch (error) {
        showToast('تعذر فتح المجلد: ' + error, 'error');
    }
}

async function applyReviews() {
    if (!currentProcessId) return;
    try {
        const result = await window.pywebview.api.apply_reviews(currentProcessId);
        showToast(`تم تنفيذ التعديلات! نجاح: ${result.success}, فشل: ${result.failed}`, 'success');
        
        // Reload stats if backend provides them
        if (result.new_stats) {
            loadResults(result.new_stats);
        }
    } catch (error) {
        showToast('حدث خطأ أثناء تنفيذ التعديلات', 'error');
    }
}

// --- History Logic ---
async function loadHistory() {
    const listEl = document.getElementById('history-list');
    listEl.innerHTML = '<div class="spinner"></div>';
    
    try {
        const history = await window.pywebview.api.get_history();
        
        if (!history || history.length === 0) {
            listEl.innerHTML = '<div class="empty-state">لا توجد عمليات سابقة.</div>';
            return;
        }
        
        listEl.innerHTML = '';
        history.forEach(item => {
            const date = new Date(item.timestamp).toLocaleString('ar-EG');
            const statusClass = item.status === 'completed' ? 'badge-completed' : 'badge-reviewing';
            const statusText = item.status === 'completed' ? 'مكتمل' : 'قيد المراجعة';
            
            const card = document.createElement('div');
            card.className = 'history-card';
            card.onclick = () => viewProcess(item.processId);
            
            card.innerHTML = `
                <div class="history-info">
                    <h4>العملية ${item.processId.substring(0,8)}...</h4>
                    <div class="history-date">${date}</div>
                    <span class="badge ${statusClass}">${statusText}</span>
                </div>
                <div class="history-stats">
                    <span>✅ ${item.stats.matched}</span>
                    <span>❌ ${item.stats.not_found}</span>
                    <span>⚠️ ${item.stats.review}</span>
                </div>
            `;
            listEl.appendChild(card);
        });
    } catch (error) {
        listEl.innerHTML = '<div class="empty-state">حدث خطأ أثناء تحميل السجل.</div>';
    }
}

async function viewProcess(processId) {
    try {
        const data = await window.pywebview.api.get_process_details(processId);
        currentProcessId = processId;
        loadResults(data.stats);
        showScreen('screen-results');
    } catch (error) {
        showToast('تعذر تحميل تفاصيل العملية', 'error');
    }
}

// --- Settings & Server Logic ---
async function loadSettings() {
    try {
        const settings = await window.pywebview.api.get_settings();
        if (settings) {
            document.getElementById('setting-unstructured-key').value = settings.unstructured_api_key || settings.unstructured_key || '';
            const profileEl = document.getElementById('setting-unstructured-profile');
            if (profileEl) profileEl.value = settings.unstructured_profile || 'balanced';
            document.getElementById('setting-local-url').value = settings.local_api_url || 'http://127.0.0.1:8000/v1/chat/completions';
            document.getElementById('setting-local-key').value = settings.local_api_key || '';
            document.getElementById('setting-model-name').value = settings.local_model || settings.model_name || 'gpt-4o-mini';
            document.getElementById('setting-msemax-dir').value = settings.msemax_dir || '';
        }
    } catch (error) {
        console.error('Failed to load settings', error);
    }
}

async function saveSettings() {
    const profileEl = document.getElementById('setting-unstructured-profile');
    const settings = {
        unstructured_api_key: document.getElementById('setting-unstructured-key').value,
        unstructured_profile: profileEl ? profileEl.value : 'balanced',
        local_api_url: document.getElementById('setting-local-url').value,
        local_api_key: document.getElementById('setting-local-key').value,
        local_model: document.getElementById('setting-model-name').value,
        msemax_dir: document.getElementById('setting-msemax-dir').value
    };
    
    try {
        await window.pywebview.api.save_settings(JSON.stringify(settings));
        showToast('تم حفظ الإعدادات بنجاح', 'success');
    } catch (error) {
        showToast('حدث خطأ أثناء حفظ الإعدادات', 'error');
    }
}

async function selectMsemaxDir() {
    try {
        const dirPath = await window.pywebview.api.select_folder();
        if (dirPath) {
            document.getElementById('setting-msemax-dir').value = dirPath;
        }
    } catch (error) {
        console.error(error);
    }
}

async function setupRequirements() {
    const statusEl = document.getElementById('req-status');
    statusEl.innerHTML = '⏳';
    try {
        await window.pywebview.api.setup_msemax_requirements();
        statusEl.innerHTML = '✅';
        showToast('تم تثبيت المتطلبات بنجاح', 'success');
    } catch (error) {
        statusEl.innerHTML = '❌';
        showToast('فشل تثبيت المتطلبات', 'error');
    }
}

async function getSession() {
    const statusEl = document.getElementById('session-status');
    statusEl.innerHTML = '⏳';
    try {
        await window.pywebview.api.get_msemax_session();
        statusEl.innerHTML = '✅';
        showToast('تم تجديد الجلسة بنجاح', 'success');
    } catch (error) {
        statusEl.innerHTML = '❌';
        showToast('فشل تجديد الجلسة', 'error');
    }
}

// --- UI Functions ---
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? 'ph-check-circle' : 'ph-warning-circle';
    toast.innerHTML = `<i class="ph-fill ${icon}"></i> <span>${message}</span>`;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

async function updateServerStatus(statusData) {
    const indicator = document.getElementById('server-indicator');
    const text = document.getElementById('server-status-text');
    const btn = document.getElementById('btn-toggle-server');
    const btnSettings = document.getElementById('btn-toggle-server-settings');
    
    let isRunning = false;
    if (statusData !== undefined) {
        isRunning = typeof statusData === 'object' ? statusData.is_running : statusData;
    } else {
        try {
            isRunning = await window.pywebview.api.is_server_running();
        } catch (error) {
            console.error('Failed to get server status', error);
            return;
        }
    }
    
    if (isRunning) {
        if (indicator) indicator.className = 'status-indicator running';
        if (text) text.textContent = 'السيرفر يعمل';
        if (btn) btn.innerHTML = '<i class="ph ph-stop"></i> إيقاف السيرفر';
        if (btnSettings) btnSettings.innerHTML = '<i class="ph ph-stop"></i> إيقاف السيرفر';
        isServerRunning = true;
    } else {
        if (indicator) indicator.className = 'status-indicator stopped';
        if (text) text.textContent = 'السيرفر متوقف';
        if (btn) btn.innerHTML = '<i class="ph ph-play"></i> تشغيل السيرفر';
        if (btnSettings) btnSettings.innerHTML = '<i class="ph ph-play"></i> تشغيل السيرفر';
        isServerRunning = false;
    }
}

async function toggleServer() {
    try {
        const isRunning = await window.pywebview.api.is_server_running();
        if (isRunning) {
            await window.pywebview.api.stop_server();
            showToast('تم إيقاف السيرفر', 'success');
        } else {
            await window.pywebview.api.start_server();
            showToast('تم تشغيل السيرفر', 'success');
        }
        updateServerStatus();
    } catch (error) {
        showToast('حدث خطأ أثناء تبديل حالة السيرفر', 'error');
    }
}

// Attach event listener for the toggle server button on the home screen
document.getElementById('btn-toggle-server').addEventListener('click', toggleServer);
