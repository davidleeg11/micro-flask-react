import React, { Component } from 'react';  // new
import ReactDOM from 'react-dom';
import axios from 'axios';
import SitesList from './components/SitesList';
import AddSite from './components/AddSite';
// import UsersList from './components/UsersList';
// import AddUser from './components/AddUser';


class App extends Component {
 
  constructor() {
    super();
    this.state = {
      sites: [],
      site: '',
      // users: [],
      // username: '',
      // email: '',
    };
    this.addSite = this.addSite.bind(this);  // new
    this.handleChange = this.handleChange.bind(this);
    // this.addUser = this.addUser.bind(this);  // new
    // this.handleChange = this.handleChange.bind(this);
  };

  componentDidMount() {
    this.getSites();
  };
  
  getSites() { 
    axios.get(`${process.env.REACT_APP_SITES_SERVICE_URL}/sites`)
    .then((res) => { this.setState({ sites: res.data.data.sites }); })
    .catch((err) => { console.log(err); });
  }

  addSite(event) {
    event.preventDefault();
    const data = {
      site: this.state.site,
    };
    axios.post(`${process.env.REACT_APP_SITES_SERVICE_URL}/sites`, data)
    .then((res) => { 
      this.getSites();
      this.setState({ site: ''});
    })
    .catch((err) => { console.log(err); });
  };

  // componentDidMount() {
  //   this.getUsers();
  // };
  
  // getUsers() { 
  //   axios.get(`${process.env.REACT_APP_USERS_SERVICE_URL}/users`)
  //   .then((res) => { this.setState({ users: res.data.data.users }); })
  //   .catch((err) => { console.log(err); });
  // }

  // addUser(event) {
  //   event.preventDefault();
  //   const data = {
  //     username: this.state.username,
  //     email: this.state.email
  //   };
  //   axios.post(`${process.env.REACT_APP_USERS_SERVICE_URL}/users`, data)
  //   .then((res) => { 
  //     this.getUsers();  // new
  //     this.setState({ username: '', email: '' });  // new
  //   })
  //   .catch((err) => { console.log(err); });
  //};

  handleChange(event) {
    const obj = {};
    obj[event.target.name] = event.target.value;
    this.setState(obj);
  };

  render() {
    return (
      <section className="section">
        <div className="container">
          <div className="columns is-centered">
            <div className="column is-half ">  {/* new */}
              <br/>
              <h1 className="title is-2">CSR Migration 0.5</h1>
              <hr/><br/>
              <AddSite
                site={this.state.site}
                addSite={this.addSite}
                handleChange={this.handleChange}  // new
              />  
              <br/><br/>  
              <SitesList sites={this.state.sites}/>
            </div>
          </div>
        </div>
      </section>
    )
  }
  //   return (
  //     <section className="section">
  //       <div className="container">
  //         <div className="columns is-centered">
  //           <div className="column is-half ">  {/* new */}
  //             <br/>
  //             <h1 className="title is-2">All Users</h1>
  //             <hr/><br/>
  //             <AddUser
  //               username={this.state.username}
  //               email={this.state.email}
  //               addUser={this.addUser}
  //               handleChange={this.handleChange}  // new
  //             />  
  //             <br/><br/>  
  //             <UsersList users={this.state.users}/>
  //           </div>
  //         </div>
  //       </div>
  //     </section>
  //   )
  // }
}

ReactDOM.render(
  <App />,
  document.getElementById('root')
);
