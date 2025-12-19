import React from 'react';
import './Footer.css';

const Footer = () => {
  return (
    <div className="footer-container">
      <div className="footer-content">
        {/* First Row - Logo and Contact */}
        <div className="footer-row">
          <img 
            className="footer-logo" 
            src="/eumetnet-logo.svg" 
            alt="EUMETNET Logo" 
          />
          <a 
            href="https://www.eumetnet.eu" 
            target="_blank" 
            rel="noopener noreferrer"
            className="footer-link"
          >
            <p>Contact information</p>
            <img className="icon" src="/icons/newtab.svg" alt="Opens in new tab" />
          </a>
        </div>

        {/* Second Row - Information Text */}
        <div className="footer-row footer-row-text">
          <div className="footer-text">
            <p className="semibold">
              Technical guidance or encounter issues {' '}
              <a 
                href="https://eumetnet.github.io/meteogate-documentation/" 
                target="_blank" 
                rel="noopener noreferrer"
              >
                MeteoGate
              </a>
            </p>
            <p className="semibold">
              If you have questions about a specific dataset, contact the appropriate Data Publisher
            </p>
          </div>
        </div>

        {/* Third Row - Copyright and Legal Links */}
        <div className="footer-row footer-bottom">
          <p className="copyright">Copyright EUMETNET SNC ©2025</p>
          <a 
            href="https://www.eumetnet.eu/legal-information" 
            target="_blank" 
            rel="noopener noreferrer"
            className="footer-link"
          >
            <p>Legal information</p>
            <img className="icon" src="/icons/newtab.svg" alt="Opens in new tab" />
          </a>
        </div>
      </div>
    </div>
  );
};

export default Footer;