import React, { forwardRef, useImperativeHandle } from "react";
import { useNavigate } from "react-router-dom"; 
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
} from "@mui/material";
import PropTypes from 'prop-types';

const LogoutModal = forwardRef(({ handleLogout }, ref) => {
  const [open, setOpen] = React.useState(false);
  const navigate = useNavigate(); 

  useImperativeHandle(ref, () => ({
    open: () => setOpen(true),
    close: () => setOpen(false),
  }));
  const handleClose = () => setOpen(false);

  const handle_Logout = async () => {
    await handleLogout(); 
    handleClose();
    navigate("/login");
  };

  return (
    <Dialog 
      open={open} 
      onClose={handleClose} 
      maxWidth="xs"
      PaperProps={{
        sx: {
          width: '100%',
          maxWidth: '400px',
        }
      }}
    >
      <DialogTitle>
        <Typography
          variant="h5"
          component="h2"
          align="center"
          sx={{ 
            fontWeight: "bold", 
            color: "text.primary"
          }}
          dir="rtl"
        >
          התנתקות
        </Typography>
      </DialogTitle>

      <DialogContent>
        <Typography
          variant="body1"
          align="center"
          sx={{ my: 2 }}
          dir="rtl"
        >
          האם את/ה בטוח/ה שברצונך להתנתק?
        </Typography>
      </DialogContent>

      <DialogActions sx={{ 
        justifyContent: "center", 
        gap: 2,
        pb: 3 
      }}>
        <Button 
          onClick={handleClose} 
          variant="outlined" 
          color="primary"
          sx={{ minWidth: 100 }}
        >
          לא
        </Button>
        <Button
          onClick={handle_Logout}
          variant="contained"
          color="error"
          sx={{ minWidth: 100 }}
        >
          כן
        </Button>
      </DialogActions>
    </Dialog>
  );
});

LogoutModal.displayName = "LogoutModal";
LogoutModal.propTypes = {
  handleLogout: PropTypes.func.isRequired, 
};

export default LogoutModal;