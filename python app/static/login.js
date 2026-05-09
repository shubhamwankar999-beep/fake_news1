document.addEventListener('DOMContentLoaded', () => {
    const signupForm = document.getElementById('signupForm');
    const loginForm = document.getElementById('loginForm');
    const otpSection = document.getElementById('otpSection');
    const statusMsg = document.getElementById('statusMsg');
    const timerCount = document.getElementById('timerCount');
    let timerInterval;

    const showMsg = (text, type = 'error') => {
        statusMsg.textContent = text;
        statusMsg.className = `message ${type}`;
        statusMsg.classList.remove('hidden');
        setTimeout(() => statusMsg.classList.add('hidden'), 5000);
    };
    
    const startTimer = (durationInSeconds) => {
        clearInterval(timerInterval);
        let timer = durationInSeconds;
        
        timerInterval = setInterval(() => {
            const minutes = Math.floor(timer / 60);
            const seconds = timer % 60;
            
            timerCount.textContent = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
            
            if (--timer < 0) {
                clearInterval(timerInterval);
                timerCount.textContent = "Expired";
                timerCount.style.color = "#ef4444";
                showMsg("OTP has expired. Please request a new one.");
            }
        }, 1000);
    };

    // Toggle Signup/Login
    document.getElementById('toLogin').onclick = (e) => { 
        e.preventDefault();
        signupForm.classList.add('hidden'); 
        loginForm.classList.remove('hidden'); 
    };
    document.getElementById('toSignup').onclick = (e) => { 
        e.preventDefault();
        loginForm.classList.add('hidden'); 
        signupForm.classList.remove('hidden'); 
    };

    // Signup logic
    document.getElementById('signupBtn').onclick = async () => {
        const name = document.getElementById('signupName').value;
        const email = document.getElementById('signupEmail').value;

        if (!name || !email) {
            showMsg("Please fill in all fields.");
            return;
        }

        try {
            const res = await fetch('/auth/signup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email, full_name: name })
            });
            const data = await res.json();
            if (res.ok) {
                showMsg(data.message, 'success');
                setTimeout(() => document.getElementById('toLogin').click(), 2000);
            } else {
                let errorMsg = data.detail;
                if (typeof errorMsg === 'object') errorMsg = JSON.stringify(errorMsg);
                showMsg(errorMsg);
            }
        } catch (err) {
            showMsg("Connection error. Is the server running?");
        }
    };

    // Request OTP logic
    document.getElementById('getOtpBtn').onclick = async () => {
        const email = document.getElementById('loginEmail').value;
        if (!email) {
            showMsg("Please enter your email address.");
            return;
        }

        try {
            const res = await fetch('/auth/request-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email })
            });
            const data = await res.json();
            if (res.ok) {
                // If the server returns the OTP (Demo simulation), let's show it
                const msg = data.otp ? `OTP received: ${data.otp}` : "OTP sent! Check terminal.";
                showMsg(msg, 'success');
                otpSection.classList.remove('hidden');
                
                // Start the 5-minute timer (300 seconds)
                startTimer(300);
            } else {
                let errorMsg = data.detail;
                if (typeof errorMsg === 'object') errorMsg = JSON.stringify(errorMsg);
                showMsg(errorMsg);
            }
        } catch (err) {
            showMsg("Connection error.");
        }
    };

    // Verify OTP logic
    document.getElementById('verifyOtpBtn').onclick = async () => {
        const email = document.getElementById('loginEmail').value;
        const otp = document.getElementById('loginOtp').value;

        if (!otp) {
            showMsg("Please enter the OTP.");
            return;
        }

        try {
            const res = await fetch('/auth/verify-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email, otp: otp })
            });
            const data = await res.json();
            if (res.ok) {
                showMsg("Login Successful! Redirecting...", 'success');
                // Store user info in localStorage for the dashboard
                localStorage.setItem('currentUser', JSON.stringify(data.user));
                
                // Redirect to dashboard
                setTimeout(() => {
                    window.location.href = '/dashboard';
                }, 1000);
            } else {
                let errorMsg = data.detail;
                if (typeof errorMsg === 'object') errorMsg = JSON.stringify(errorMsg);
                showMsg(errorMsg);
            }
        } catch (err) {
            showMsg("Login failed. Please try again.");
        }
    };
});
