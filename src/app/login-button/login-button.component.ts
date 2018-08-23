import { Component, OnInit } from '@angular/core';
import { AngularFireAuth } from 'angularfire2/auth';
import { auth } from 'firebase';

@Component({
  selector: 'app-login-button',
  templateUrl: './login-button.component.html',
  styleUrls: ['./login-button.component.css']
})
export class LoginButtonComponent implements OnInit {

  constructor(public fireAuth: AngularFireAuth) { }
  signedIn = false;

  ngOnInit() {
  }
  login() {
    this.fireAuth.auth.signInWithPopup(new auth.GoogleAuthProvider());
  }
  logout() {
    this.fireAuth.auth.signOut();
  }

}
