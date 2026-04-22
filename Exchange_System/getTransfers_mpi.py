from mpi4py import MPI
import numpy as np
from app.run import socketio, app
from app.models import Transfer, User


@socketio.on("all_transfer_notification")
def handle_all_transfer_notification(data):
    print("Received all_transfer_notification event:")
    print("Message:", data["message"])
    print("Transfer:", data["transfer"])
    print("Transfered:", data["transfered"])


with app.app_context():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    users = User.query.all()
    total_received_trans = None
    total_send_trans = None
    for user in users:
        print("user->", user.username)
        if rank == 0:
            total_send_trans = np.array(
                object=Transfer.getSenderTrans(sender=user.username)
            ).sum()
            print("total_send_trans=", total_send_trans)
        elif rank == 1:
            total_received_trans = np.array(
                object=Transfer.getReceiverTrans(receiver=user.username)
            ).sum()

            print("total_received_trans=", total_received_trans)

    # Print or log before emitting
    print("Before emitting to socketio")

    res = socketio.emit(
        "all_transfer_notification",
        {
            "message": "Transfer Hi!",
            "transfer": total_send_trans,
            "transfered": total_received_trans,
        },
    )
    # Print or log after emitting
    print("After emitting to socketio", res)
