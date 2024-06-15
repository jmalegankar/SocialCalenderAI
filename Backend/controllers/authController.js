const jwt = require("jsonwebtoken"); //Send user token for login useful to authentication
const crypto = require("crypto");
//Model for CRUD Options
const User = require("../models/user");
const filterObj = require("../utils/filterObj");
const { promisify } = require("util");
const otpGenerator = require("otp-generator");
const resetPassword = require("../Templates/Mail/resetPassword");
const otp = require("../Templates/Mail/otp");
const path = require("path");
const fs = require("fs");

const signToken = (userId) => {
  return jwt.sign({ userId }, process.env.JWT_SECRET);
};
const mailService = require("../services/mailer");
//Sign Up => Register - SendOTP - verifyOTP

//api.tawk.com/auth/register

//Register New User
exports.register = async (req, res, next) => {
  console.log("Processing:", req.body);
  const { username, emailID, password, passwordConfirm } = req.body;

  const filteredBody = filterObj(
    req.body,
    "username",
    "emailID",
    "password",
    "passwordConfirm"
  );

  //check if a verified user with given email exists
  const existing_user = await User.findOne({ emailID: emailID });

  if (existing_user && existing_user.verified) {
    res.status(400).json({
      status: "error",
      message: "Email is already in use, Please login.",
    });
  } else if (existing_user) {
    await User.findOneAndUpdate({ emailID: emailID }, filteredBody, {
      new: true,
      validateModifiedOnly: true,
    });

    req.userId = existing_user._id;
    next();
  } else {
    //If user record is not available in DB
    const new_user = await User.create(filteredBody);

    //generate OTP and send email to user
    req.userId = new_user._id;
    next();
  }
};
//Send OTP
exports.sendOTP = async (req, res, next) => {
  const { userId } = req;
  const new_otp = otpGenerator.generate(6, {
    lowerCaseAlphabets: false,
    upperCaseAlphabets: false,
    specialChars: false,
  });

  const otp_expiry_time = Date.now() + 10 * 60 * 1000; //10mins after otp is sent

  //
  const user = await User.findByIdAndUpdate(userId, {
    otp_expiry_time,
  });

  user.otp = new_otp.toString();

  await user.save({ new: true, validateModifiedOnly: true });
  console.log(new_otp);
  //Send Mail
  try {
    mailService.sendEmail({
      sender: "mailtrap@demomailtrap.com",
      recipient: "praneethchitturi12@gmail.com", //user.email,
      subject: "Verification OTP",
      html: otp(user.username, new_otp),
      attachments: [],
    });
  } catch (error) {
    console.log(error);
    res.status(500).json({
      status: "error",
      message: "OTP not sent Successfully!",
    });
  }

  /*.then(()=>{

    }).catch((err)=>{
        res.status(500).json({
            status:"error",
            message:"OTP not sent Successfully!"
        })
    })*/

  res.status(200).json({
    status: "success",
    message: "OTP sent Successfully!",
  });
};

exports.verifyOTP = async (req, res, next) => {
  //Verify OTP and update user record accordingly
  const { emailID, otp } = req.body;

  const user = await User.findOne({
    emailID,
    otp_expiry_time: { $gt: Date.now() },
  });

  if (!user) {
    res.status(400).json({
      status: "error",
      message: "Email is Invalid or OTP expired",
    });
  }
  if (user.verified) {
    return res.status(400).json({
      status: "error",
      message: "Email is already verified",
    });
  }
  if (!(await user.correctOTP(otp, user.otp))) {
    res.status(400).json({
      status: "error",
      message: "OTP is incorrect",
    });
    return;
  }

  //OTP is correct
  user.verified = true;
  user.otp = undefined;

  await user.save({ new: true, validateModifiedOnly: true });

  const token = signToken(user._id);
  res.cookie("jwt", token, {
    maxAge: 15 * 24 * 60 * 60 * 1000,
    httpOnly: true,
    sameSite: "strict",
  });
  res.status(200).json({
    status: "success",
    message: "OTP verified Successfully!",
    token,
    user_id: user._id,
  });
};
//Login User
exports.login = async (req, res, next) => {
  const { emailID, password } = req.body;

  if (!emailID || !password) {
    res.status(400).json({
      status: "error",
      message: "Both email and password are required",
    });
    return;
  }

  const userDoc = await User.findOne({ emailID: emailID }).select("+password");

  if (
    !userDoc ||
    !(await userDoc.correctPassword(password, userDoc.password))
  ) {
    res.status(400).json({
      status: "error",
      message: "Email or password is incorrect",
    });
    return;
  }

  const token = signToken(userDoc._id);
  res.cookie("jwt", token, {
    maxAge: 15 * 24 * 60 * 60 * 1000,
    httpOnly: true,
    sameSite: "strict",
  });
  res.status(200).json({
    status: "success",
    message: "Logged in successfully",
    token,
    user_id: userDoc._id,
  });
};

//Make  sure users who logged in are accessing
//Two types of Routes -> Protected (Only logged in Users can access)
//                    -> UnProtected (Public can access; anybody)
exports.protect = async (req, res, next) => {
  //1) Getting Token (JWT) and check if its there
  let token;

  // 'Bearer ksdlabsddksmd'
  if (
    req.headers.authorization &&
    req.headers.authorization.startsWith("Bearer")
  ) {
    token = req.headers.authorization.split(" ")[1];
  } else if (req.headers.cookie) {
    //Sometimes can be sent in cookies
    token = req.headers.cookie.replace("jwt=", "");
  } else {
    res.status(400).json({
      status: "error",
      message: "You are not logged in! Please log in to get access",
    });
    return;
  }
  //2) Verify if Token is correct or not
  const decoded = await promisify(jwt.verify)(token, process.env.JWT_SECRET);

  //3) Check if user still exist
  const this_user = await User.findById(decoded.userId);

  if (!this_user) {
    res.status(400).json({
      status: "error",
      message: "The user belonging to this token doesn't exist",
    });
    return;
  }

  //4) Check if user changed their password after token was issued
  if (this_user.changedPasswordAfter(decoded.iat)) {
    res.status(400).json({
      status: "error",
      message: "User recently updated Password! Please log in again",
    });
  }

  //Pass control to next middleware
  req.user = this_user;
  next();
};

//Reset Password
exports.forgotPassword = async (req, res, next) => {
  //1) Get Users email
  const user = await User.findOne({ emailID: req.body.emailID });

  if (!user) {
    return res.status(400).json({
      status: "error",
      message: "There is no user with given Email Address",
    });
  }

  //2) Generate random reset token
  const resetToken = user.createPasswordResetToken();

  const resetURL = `http://localhost:3000/auth/new-password?token=${resetToken}`;

  user.passwordResetToken = crypto
    .createHash("sha256")
    .update(resetToken)
    .digest("hex");
  user.passwordResetExpires = Date.now() + 10 * 60 * 1000;
  await user.save({ new: true, validateModifiedOnly: true });
  console.log(resetURL, resetToken);
  try {
    //Sending Email with resetURL to User
    mailService.sendEmail({
      sender: "mailtrap@demomailtrap.com",
      recipient: "praneethchitturi12@gmail.com",
      subject: "Reset Password",
      html: resetPassword(user.username, resetURL),
      attachments: [],
    });

    res.status(200).json({
      status: "success",
      message: "Reset Password Link sent to Email",
    });
  } catch (error) {
    //If error in sending mail, reset token in backend db
    user.passwordResetToken = undefined;
    user.passwordResetExpires = undefined;

    await user.save({ validateBeforeSave: false });

    return res.status(500).json({
      status: "error",
      message: "There was an error sending the email, Please try again later.",
    });
  }
};

exports.resetPassword = async (req, res, next) => {
  //1) Get User based on token
  const hashedToken = crypto
    .createHash("sha256")
    .update(req.body.token)
    .digest("hex");
  //const hashedToken =req.body.token
  const user = await User.findOne({
    passwordResetToken: hashedToken,
    passwordResetExpires: { $gt: Date.now() },
  });

  //2) If token has expired or user is out of time window
  if (!user) {
    return res.status(400).json({
      status: "error",
      message: "Token is invalid or Expired",
    });
  }

  //3) Updating Password and nulling our resetTokens
  user.password = req.body.password;
  user.passwordConfirm = req.body.passwordConfirm;
  user.passwordResetToken = undefined;
  user.passwordResetExpires = undefined;

  //3) Actually saving the new update
  await user.save();

  //Send an Email to user informing about Password Reset

  //4) Log in the user and send new JWT
  const token = signToken(user._id);
  res.cookie("jwt", token, {
    maxAge: 15 * 24 * 60 * 60 * 1000,
    httpOnly: true,
    sameSite: "strict",
  });
  res.status(200).json({
    status: "success",
    message: "Password Reset Succesfull",
    token,
  });
};
