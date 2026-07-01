const API_URL = 'http://127.0.0.1:5000/api/habits';

document.addEventListener('DOMContentLoaded', fetchHabits);

async function fetchHabits() {
    try {
        const response = await fetch(API_URL);
        const habits = await response.json();
        const tbody = document.getElementById('habitTableBody');
        tbody.innerHTML = '';
        
        habits.forEach(habit => {
            const tr = document.createElement('tr');
            
            // Cột Done? trạng thái hiện tại
            const doneSection = habit.completed_today 
                ? `<div class="checkbox-container" onclick="toggleHabit(${habit.id})">
                    <input type="checkbox" checked> <span class="done-label">✓ Today</span>
                   </div>`
                : `<div class="checkbox-container" onclick="toggleHabit(${habit.id})">
                    <input type="checkbox">
                   </div>`;

            // Vẽ lưới HabitKit mini (Mặc định 60 ô vuông)
            let gridHtml = '<div class="habitkit-mini-grid">';
            const totalDots = 60; 
            for (let i = 0; i < totalDots; i++) {
                let isDotActive = false;
                // Nếu có streak, tô xám đậm các ô cuối từ phải qua trái. Nếu streak = 0, trống hết.
                if (habit.streak > 0 && i >= (totalDots - habit.streak)) {
                    isDotActive = true;
                }
                gridHtml += `<span class="mini-dot ${isDotActive ? 'active' : ''}"></span>`;
            }
            gridHtml += '</div>';

            // Đổ toàn bộ dữ liệu vào dòng
            tr.innerHTML = `
                <td style="font-weight: 500;">${habit.name}</td>
                <td>
                    <span class="desc-text">${habit.description || '<i>Không có mô tả</i>'}</span>
                    <span class="date-text">📅 Tạo: ${habit.created_at}</span>
                </td>
                <td>${doneSection}</td>
                <td><button class="btn-done" onclick="toggleHabit(${habit.id})">Done</button></td>
                <td>${gridHtml}</td>
                <td class="streak-text">🔥 ${habit.streak} ngày</td>
                <td><button class="btn-delete" onclick="deleteHabit(${habit.id})">🗑️</button></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error("Lỗi đồng bộ dữ liệu với Backend:", error);
    }
}

async function addHabit() {
    const nameInput = document.getElementById('habitInput');
    const descInput = document.getElementById('descInput');
    if (!nameInput.value.trim()) return;

    await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            name: nameInput.value,
            description: descInput.value 
        })
    });

    nameInput.value = '';
    descInput.value = '';
    fetchHabits();
}

async function toggleHabit(id) {
    await fetch(`${API_URL}/${id}/toggle`, { method: 'POST' });
    fetchHabits();
}

async function deleteHabit(id) {
    if (confirm("Bạn có chắc chắn muốn xóa thói quen này không?")) {
        await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
        fetchHabits();
    }
}