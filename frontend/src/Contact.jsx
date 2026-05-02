import React from 'react';
import { Link } from 'react-router-dom';
import './Contact.css';

const Contact = () => {
  return (
    <div className="clinical-app">
      {/* 1. NAVBAR */}
      <nav className="navbar glass">
        <div className="nav-brand">
          <span className="logo-icon">⚕️</span>
          <span className="app-name">MedBrief AI</span>
        </div>
        <div className="nav-links">
          <Link to="/">Home</Link>
          <a href="/#features">Features</a>
          <a href="/#about">About</a>
          <Link to="/contact" className="active">Contact</Link>
        </div>
      </nav>

      {/* 2. CONTACT HERO */}
      <section className="contact-hero">
        <div className="glow-shape shape-1"></div>
        <div className="glow-shape shape-2"></div>
        <div className="hero-text fade-in">
          <h1 className="gradient-text">Get in Touch</h1>
          <p className="subheading">
            Have questions about our Agentic AI workflow or integration? 
            Reach out to us directly.
          </p>
        </div>
      </section>

      {/* 3. CONTACT CONTENT */}
      <section className="contact-container">
        <div className="contact-grid">

          {/* Contact Info Only */}
          <div className="contact-info center-card">
            <div className="info-card glass hover-elevate">
              <div className="icon">📧</div>
              <h4>Email</h4>
              <p>support@clinicalai.demo</p>
            </div>

            <div className="info-card glass hover-elevate">
              <div className="icon">📞</div>
              <h4>Contact Number</h4>
              <p>+91 98765 43210</p>
            </div>
          </div>

        </div>
      </section>

      {/* 4. FOOTER */}
      <footer className="footer">
        <div className="footer-bottom">
          <p>&copy; 2026 MedBrief AI.</p>
        </div>
      </footer>
    </div>
  );
};

export default Contact;