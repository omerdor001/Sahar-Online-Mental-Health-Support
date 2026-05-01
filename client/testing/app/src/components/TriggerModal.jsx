import { Modal, Box, Typography, Button } from '@mui/material';
import PropTypes from 'prop-types';

const TriggerModal = ({ isOpen, message, onClose }) => {
  return (
    <Modal
      open={isOpen}
      onClose={onClose}
      sx={{
        display: 'flex',
        alignItems: 'flex-end',
        justifyContent: 'center',
        bottom: 0,
        left: 0,
        right: 0,
      }}
    >
      <Box
        sx={{
          width: '100%',
          maxWidth: 400,
          backgroundColor: 'white',
          borderRadius: 2,
          boxShadow: 24,
          p: 3,
          mb: 2,
          border: '2px solid #ff5722',
        }}
      >
        <Typography
          variant="h6"
          gutterBottom
          sx={{ fontWeight: 'bold', color: '#ff5722' }}
        >
          {message}
        </Typography>
        <Button
          onClick={onClose}
          variant="contained"
          color="primary"
          fullWidth
          sx={{ mt: 2 }}
        >
          סגור
        </Button>
      </Box>
    </Modal>
  );
};

export default TriggerModal;
TriggerModal.propTypes = {
  isOpen: PropTypes.func.isRequired, 
  message: PropTypes.func.isRequired,
  onClose: PropTypes.func.isRequired
};
