/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/js/**/*.js",
    "./accounts/forms.py",
    "./portfolio/forms.py",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#2563EB',
        'primary-light': '#3B82F6',
        'primary-dark': '#1D4ED8',
        'primary-soft': 'rgba(37, 99, 235, 0.08)',
        
        secondary: '#7C3AED',
        'secondary-light': '#8B5CF6',
        'secondary-dark': '#6D28D9',
        'secondary-soft': 'rgba(124, 58, 237, 0.08)',
        
        accent: '#06B6D4',
        'accent-light': '#22D3EE',
        'accent-dark': '#0891B2',
        'accent-soft': 'rgba(6, 182, 212, 0.08)',
        
        success: '#10B981',
        'success-light': '#34D399',
        'success-dark': '#059669',
        'success-soft': 'rgba(16, 185, 129, 0.08)',
        
        warning: '#F59E0B',
        'warning-light': '#FBBF24',
        'warning-dark': '#D97706',
        'warning-soft': 'rgba(245, 158, 11, 0.08)',
        
        danger: '#EF4444',
        'danger-light': '#F87171',
        'danger-dark': '#DC2626',
        'danger-soft': 'rgba(239, 68, 68, 0.08)',
        
        dark: '#0F172A',
        light: '#F8FAFC',
      },
      fontFamily: {
        sans: ['Inter', 'Poppins', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        soft: '0 10px 30px -10px rgba(0, 0, 0, 0.06)',
        card: '0 8px 32px 0 rgba(31, 38, 135, 0.04)',
        premium: '0 20px 48px 0 rgba(31, 38, 135, 0.08), 0 10px 30px -10px rgba(0, 0, 0, 0.08)',
      },
      borderRadius: {
        'card': '1rem',
      },
      animation: {
        float: 'float 6s ease-in-out infinite',
        'fade-in': 'fadeIn 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards',
        'slide-up': 'slideUp 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        fadeIn: {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        slideUp: {
          from: { transform: 'translateY(20px)', opacity: '0' },
          to: { transform: 'translateY(0)', opacity: '1' },
        },
      }
    },
  },
  plugins: [],
}
