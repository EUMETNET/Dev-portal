import './Header.css';

const Header = () => {
  return (
    <div>
      <div className="grid mb-4">
        <div className="col-12 md:col-3 flex align-items-center justify-content-center md:justify-content-start md:pl-6 md:pt-4 flex-order-3 md:flex-order-1">
          <img src="/eumetnet_femdi.png" alt="EUMETNET FEMDI" className="header-logo" />
        </div>
        <div className="col-12 px-4 md:col-6 flex align-items-center justify-content-center flex-column flex-order-1 md:flex-order-2">
          <h1 className="md:mt-6">Developer Portal prototype</h1>
          <h1 id="app-header-2" className="mt-0 md:mt-4">
            Secured with Keycloak
          </h1>
        </div>
        <div className="col-12 md:col-3 flex align-items-center justify-content-center md:justify-content-end md:pr-6 md:pt-4 flex-order-4 md:flex-order-3">
          <img src="/co-funded_by_the_eu.jpg" alt="Co-Funded by the EU" className="header-logo" />
        </div>
      </div>
    </div>
  );
};

export default Header;
