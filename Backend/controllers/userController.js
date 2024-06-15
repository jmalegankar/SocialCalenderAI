const User = require("../models/user");
const filterObj = require("../utils/filterObj");

//Sign Up => Register - SendOTP - verifyOTP

//api.tawk.com/auth/register


//Register New User
exports.profilesetup = async(req,res,next)=>{
    const {user} = req;
    const filteredBody = filterObj(req.body,"availability","preferences","location")
    //check if a verified user with given email exists
    const updated_user = await User.findByIdAndUpdate(user._id,{...filteredBody,profileSetup:true},{
        new: true,validateModifiedOnly:true
    })
    
    res.status(200).json({
        status:"success",
        data:updated_user,
        message:"Profile updated Successfully!",
    })

}