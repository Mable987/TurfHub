// Gradient Wave Login Form JavaScript
class GradientWaveLoginForm {
    constructor() {
        thisaform = document.getElementById('loginForm');
        this.emailInput = document.getElementById('email');
        this.passwordInput = document.getElementById('password');
        this.passwordToggle = document.getElementById('passwordToggle');
        this.submitButton = this.form.querySelector('.gradient-button');
        this.successMessage = document.getElementById('successMessage');
        this.socialButtons = document.querySelectorAll('.social-btn');
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.setupPasswordToggle();
        this.setupSocialButtons();
        this.setupWaveEffects();
        this.setupRippleEffects();
    }
    
    bindEvents() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        this.emailInput.addEventListener('blur', () => this.validateEmail());
        this.passwordInput.addEventListener('blur', () => this.validatePassword());
        this.emailInput.addEventListener('input', () => this.clearError('email'));
        this.passwordInput.addEventListener('input', () => this.clearError('password'));
        
        // Add wave effects to inputs
        [this.emailInput, this.passwordInput].forEach(input => {
            input.addEventListener('focus', (e) => this.triggerInputWave(e));
            input.addEventListener('blur', (e) => this.resetInputWave(e));
        });
    }
    
    setupPasswordToggle() {
        this.passwordToggle.addEventListener('click', () => {
            const type = this.passwordInput.type === 'password' ? 'text' : 'password';
            this.passwordInput.type = type;
            
            this.passwordToggle.classList.toggle('show-password', type === 'text');
            
            // Add ripple effect to toggle
            this.createRipple(event, this.passwordToggle);
        });
    }
    
    setupSocialButtons() {
        this.socialButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                this.createRipple(e, button);
                
                // Determine provider from button class or SVG
                let provider = 'Social';
                if (button.querySelector('.google-bg')) provider = 'Google';
                else if (button.querySelector('.facebook-bg')) provider = 'Facebook';
                else if (button.querySelector('.apple-bg')) provider = 'Apple';
                
                this.handleSocialLogin(provider, button);
            });
        });
    }
    
    setupWaveEffects() {
        // Add interactive wave effects to card
        const card = document.querySelector('.login-card');
        card.addEventListener('mousemove', (e) => {
            this.updateCardWave(e, card);
        });
        
        // Add floating animation to particles
        this.animateParticles();
    }
    
    setupRippleEffects() {
        // Add ripple to main button
        this.submitButton.addEventListener('click', (e) => {
            this.createRipple(e, this.submitButton.querySelector('.button-ripple'));
        });
        
        // Add ripple to checkbox
        const checkbox = document.querySelector('.checkbox-container');
        checkbox.addEventListener('click', (e) => {
            this.createGradientRipple(e, checkbox);
        });
    }
    
    updateCardWave(e, card) {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const deltaX = (x - centerX) / centerX;
        const deltaY = (y - centerY) / centerY;
        
        const tiltX = deltaY * 5;
        const tiltY = -deltaX * 5;
        
        card.style.transform = `perspective(1000px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) translateY(-5px)`;
    }
    
    animateParticles() {
        const particles = document.querySelectorAll('.particle');
        particles.forEach((particle, index) => {
            // Add random movement
            setInterval(() => {
                const randomX = Math.random() * 20 - 10;
                const randomY = Math.random() * 20 - 10;
                particle.style.transform = `translate(${randomX}px, ${randomY}px)`;
            }, 2000 + index * 500);
        });
    }
    
    triggerInputWave(e) {
        const container = e.target.closest('.input-container');
        const wave = container.querySelector('.input-wave');
        
        // Reset and trigger wave animation
        wave.style.animation = 'none';
        setTimeout(() => {
            wave.style.animation = 'inputWaveFlow 1s ease-in-out';
        }, 10);
        
        // Add glow effect
        container.style.boxShadow = '0 0 30px rgba(255, 255, 255, 0.2)';
    }
    
    resetInputWave(e) {
        const container = e.target.closest('.input-container');
        container.style.boxShadow = '';
    }
    
    createRipple(event, element) {
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        const ripple = document.createElement('div');
        ripple.style.cssText = `
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: scale(0);
            animation: rippleAnimation 0.6s linear;
            left: ${x}px;
            top: ${y}px;
            width: ${size}px;
            height: ${size}px;
            pointer-events: none;
        `;
        
        element.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
        
        // Add ripple animation if not exists
        if (!document.querySelector('#ripple-keyframes')) {
            const style = document.createElement('style');
            style.id = 'ripple-keyframes';
            style.textContent = `
                @keyframes rippleAnimation {
                    to {
                        transform: scale(4);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    createGradientRipple(event, element) {
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height) * 2;
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        const ripple = document.createElement('div');
        ripple.style.cssText = `
            position: absolute;
            border-radius: 50%;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.3), rgba(118, 75, 162, 0.3));
            transform: scale(0);
            animation: gradientRipple 0.8s ease-out;
            left: ${x}px;
            top: ${y}px;
            width: ${size}px;
            height: ${size}px;
            pointer-events: none;
            z-index: 0;
        `;
        
        element.style.position = 'relative';
        element.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 800);
        
        // Add gradient ripple animation
        if (!document.querySelector('#gradient-ripple-keyframes')) {
            const style = document.createElement('style');
            style.id = 'gradient-ripple-keyframes';
            style.textContent = `
                @keyframes gradientRipple {
                    to {
                        transform: scale(1);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    validateEmail() {
        const email = this.emailInput.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (!email) {
            this.showError('email', 'Email address is required');
            return false;
        }
        
        if (!emailRegex.test(email)) {
            this.showError('email', 'Please enter a valid email address');
            return false;
        }
        
        this.clearError('email');
        return true;
    }
    
    validatePassword() {
        const password = this.passwordInput.value;
        
        if (!password) {
            this.showError('password', 'Password is required');
            return false;
        }
        
        if (password.length < 6) {
            this.showError('password', 'Password must be at least 6 characters long');
            return false;
        }
        
        this.clearError('password');
        return true;
    }
    
    showError(field, message) {
        const formGroup = document.getElementById(field).closest('.form-group');
        const errorElement = document.getElementById(`${field}Error`);
        
        formGroup.classList.add('error');
        errorElement.textContent = message;
        errorElement.classList.add('show');
        
        // Add wave shake animation
        const inputContainer = formGroup.querySelector('.input-container');
        inputContainer.style.animation = 'waveShake 0.5s ease-in-out';
        setTimeout(() => {
            inputContainer.style.animation = '';
        }, 500);
        
        // Create error wave effect
        this.createErrorWave(inputContainer);
    }
    
    clearError(field) {
        const formGroup = document.getElementById(field).closest('.form-group');
        const errorElement = document.getElementById(`${field}Error`);
        
        formGroup.classList.remove('error');
        errorElement.classList.remove('show');
        setTimeout(() => {
            errorElement.textContent = '';
        }, 300);
    }
    
    createErrorWave(element) {
        const wave = document.createElement('div');
        wave.style.cssText = `
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 107, 107, 0.3), transparent);
            animation: errorWaveMove 0.8s ease-out;
            border-radius: 16px;
            pointer-events: none;
            z-index: 1;
        `;
        
        element.style.position = 'relative';
        element.appendChild(wave);
        
        setTimeout(() => {
            wave.remove();
        }, 800);
        
        // Add error wave animation
        if (!document.querySelector('#error-wave-keyframes')) {
            const style = document.createElement('style');
            style.id = 'error-wave-keyframes';
            style.textContent = `
                @keyframes errorWaveMove {
                    0% { left: -100%; }
                    100% { left: 100%; }
                }
                
                @keyframes waveShake {
                    0%, 100% { transform: translateX(0); }
                    25% { transform: translateX(-5px); }
                    75% { transform: translateX(5px); }
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        
        const isEmailValid = this.validateEmail();
        const isPasswordValid = this.validatePassword();
        
        if (!isEmailValid || !isPasswordValid) {
            // Add button shake effect
            this.submitButton.style.animation = 'waveShake 0.5s ease-in-out';
            setTimeout(() => {
                this.submitButton.style.animation = '';
            }, 500);
            return;
        }
        
        this.setLoading(true);
        
        try {
            // Simulate gradient wave authentication
            await new Promise(resolve => setTimeout(resolve, 2500));
            
            // Show wave success
            this.showWaveSuccess();
        } catch (error) {
            this.showError('password', 'Authentication failed. Please try again.');
        } finally {
            this.setLoading(false);
        }
    }
    
    async handleSocialLogin(provider, button) {
        console.log(`Initiating ${provider} authentication...`);
        
        // Add loading wave effect
        const wave = document.createElement('div');
        wave.style.cssText = `
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            animation: socialWaveMove 1.5s ease-in-out infinite;
            border-radius: 14px;
            pointer-events: none;
        `;
        
        button.style.position = 'relative';
        button.appendChild(wave);
        button.style.pointerEvents = 'none';
        
        try {
            await new Promise(resolve => setTimeout(resolve, 1500));
            console.log(`Redirecting to ${provider} authentication...`);
            // window.location.href = `/auth/${provider.toLowerCase()}`;
        } catch (error) {
            console.error(`${provider} authentication failed: ${error.message}`);
        } finally {
            wave.remove();
            button.style.pointerEvents = 'auto';
        }
        
        // Add social wave animation
        if (!document.querySelector('#social-wave-keyframes')) {
            const style = document.createElement('style');
            style.id = 'social-wave-keyframes';
            style.textContent = `
                @keyframes socialWaveMove {
                    0% { left: -100%; }
                    100% { left: 100%; }
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    setLoading(loading) {
        this.submitButton.classList.toggle('loading', loading);
        this.submitButton.disabled = loading;
        
        // Disable social buttons with wave effect
        this.socialButtons.forEach(button => {
            button.style.pointerEvents = loading ? 'none' : 'auto';
            button.style.opacity = loading ? '0.6' : '1';
        });
    }
    
    showWaveSuccess() {
        // Add success wave to entire form
        const card = document.querySelector('.login-card');
        const successWave = document.createElement('div');
        successWave.style.cssText = `
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(79, 172, 254, 0.3), transparent);
            animation: successCardWave 2s ease-in-out;
            border-radius: 24px;
            pointer-events: none;
            z-index: 5;
        `;
        
        card.style.position = 'relative';
        card.appendChild(successWave);
        
        // Fade out form
        this.form.style.transform = 'scale(0.95)';
        this.form.style.opacity = '0';
        
        setTimeout(() => {
            this.form.style.display = 'none';
            document.querySelector('.social-login').style.display = 'none';
            document.querySelector('.signup-link').style.display = 'none';
            
            // Show success with wave animation
            this.successMessage.classList.add('show');
            
            // Trigger success wave
            const successMessageWave = this.successMessage.querySelector('.success-wave');
            successMessageWave.style.animation = 'successWaveMove 2s ease-in-out';
            
        }, 300);
        
        // Clean up and redirect
        setTimeout(() => {
            successWave.remove();
            console.log('Redirecting to dashboard...');
            // window.location.href = '/dashboard';
        }, 3000);
        
        // Add success wave animation
        if (!document.querySelector('#success-wave-keyframes')) {
            const style = document.createElement('style');
            style.id = 'success-wave-keyframes';
            style.textContent = `
                @keyframes successCardWave {
                    0% { left: -100%; }
                    100% { left: 100%; }
                }
            `;
            document.head.appendChild(style);
        }
    }
}

// Initialize the form when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new GradientWaveLoginForm();
});