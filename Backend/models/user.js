const mongoose = require("mongoose")
const bcrypt = require("bcryptjs")
const crypto = require("crypto")

const userSchema = new mongoose.Schema({
    username:{
        type:String,
        required: [true,"UserName is required"]
    },
    avatar:{
        type:String
    },
    emailID:{
        type:String,
        required:[true,"EmailAddress is required"],
        validate: {
            validator:function (email){
                return String(email).toLowerCase().match(
                    /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
                )
            },
            message:(props)=> `Email (${props.value}) is invalid!`,
        },
    },
    password:{
        type:String,
    },
    passwordConfirm:{
        type:String,
    },
    passwordChangedAt:{
        type:Date,
    },
    passwordResetToken:{
        type:String,
    },
    passwordResetExpires:{
        type:Date,
    },
    createdAt:{
        type:Date,
    },
    updatedAt:{
        type:Date,
    },
    verified:{
        type:Boolean,
        default:false,
    },
    otp:{
        type:String,
    },
    otp_expiry_time:{
        type:Date
    },
    socket_id:{
        type:String,
    },
    friendsList:[
        {
            type:mongoose.Schema.ObjectId,
            ref:"User"
        }
    ],
    status:{
        type:String,
        enum:["Online","Offline"]
    },
    location:{
        lat:{
            type:mongoose.Types.Decimal128
            },
        long:{
            type:mongoose.Types.Decimal128
            }
        }
    ,
    availability:{
        mon:[
                    {
                        from:{
                            hour:{
                                type:String
                            },
                            min:{
                                type:String
                            }
                            },
                        to:{
                            hour:{
                                type:String
                            },
                            min:{
                                type:String
                            }
                            }
                    }        
            ],
        tues:[
                {
                    from:{
                        hour:{
                            type:String
                        },
                        min:{
                            type:String
                        }
                        },
                    to:{
                        hour:{
                            type:String
                        },
                        min:{
                            type:String
                        }
                        }
                }        
        ],
        wed:[
            {
                from:{
                    hour:{
                        type:String
                    },
                    min:{
                        type:String
                    }
                    },
                to:{
                    hour:{
                        type:String
                    },
                    min:{
                        type:String
                    }
                    }
            }        
        ],
        thurs:[
            {
                from:{
                    hour:{
                        type:String
                    },
                    min:{
                        type:String
                    }
                    },
                to:{
                    hour:{
                        type:String
                    },
                    min:{
                        type:String
                    }
                    }
            }        
        ],
        fri:[
            {
                from:{
                    hour:{
                        type:String
                    },
                    min:{
                        type:String
                    }
                    },
                to:{
                    hour:{
                        type:String
                    },
                    min:{
                        type:String
                    }
                    }
            }        
        ],
        sat:[
            {
                from:{
                    hour:{
                        type:String
                    },
                    min:{
                        type:String
                    }
                    },
                to:{
                    hour:{
                        type:String
                    },
                    min:{
                        type:String
                    }
                    }
            }        
        ],
        sun:[
            {
                from:{
                    hour:{
                        type:String
                    },
                    min:{
                        type:String
                    }
                    },
                to:{
                    hour:{
                        type:String
                    },
                    min:{
                        type:String
                    }
                    }
            }        
        ],
        
    },
    preferences:{
        foodPref:[
            {
                type:String,
            }
        ],
        eventsPref:[
            {
                type:String,
            }

        ]
    },
    profileSetup:{
        type:Boolean,
        default:false,
    }
});

userSchema.pre("save",async function(next){
    //Only run this fxn if OTP is actually modified
    if (!this.isModified("otp") || !this.otp) return next();

    //Hash the OTP with the cost of 12
    this.otp = await bcrypt.hash(this.otp.toString(),12);
    
    next();
})

userSchema.pre("save",async function(next){
    //Only run this fxn if OTP is actually modified
    if (!this.isModified("password") || !this.password || !this.isModified("passwordConfirm") || !this.passwordConfirm) return next();

    //Hash the OTP with the cost of 12
    hashedpass = await bcrypt.hash(this.password.toString(),12);
    this.password = hashedpass
    this.passwordConfirm = hashedpass
    next();
})

userSchema.methods.correctOTP = async function (candidateOTP, userOTP) {
    
    console.log(candidateOTP,userOTP)
    return await bcrypt.compare(candidateOTP, userOTP);
  };

userSchema.methods.correctPassword = async function (
    candidatePassword,
    userPassword
  ) {
    return await bcrypt.compare(candidatePassword, userPassword);
  };

userSchema.methods.createPasswordResetToken = function () {
    const resetToken = crypto.randomBytes(32).toString("hex");
  
    this.passwordResetToken = crypto
      .createHash("sha256")
      .update(resetToken)
      .digest("hex");
  
    this.passwordResetExpires = Date.now() + 10 * 60 * 1000;
  
    return resetToken;
  };


userSchema.methods.changedPasswordAfter = function (timestamp) {
    if (this.passwordChangedAt) {
      const changedTimeStamp = parseInt(
        this.passwordChangedAt.getTime() / 1000,
        10
      );
      return timestamp < changedTimeStamp;
    }
  
    // FALSE MEANS NOT CHANGED
    return false;
  };

const User = new mongoose.model("users", userSchema);
module.exports = User;