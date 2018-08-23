import { Component, OnInit } from '@angular/core';
import { AngularFireAuth } from 'angularfire2/auth';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-login-button',
  templateUrl: './login-button.component.html',
  styleUrls: ['./login-button.component.css'],
  providers: [AuthService],
})
export class LoginButtonComponent implements OnInit {

  constructor(public auth: AuthService) { }

  ngOnInit() {
  }
}
