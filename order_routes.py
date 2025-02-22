from fastapi import APIRouter, Depends, status
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.sql.functions import current_user

from models import User, Order
from schemas import OrderModel, OrderStatusModel
from fastapi.exceptions import HTTPException
from database import Session, engine
from fastapi.encoders import jsonable_encoder



order_router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)
session = Session(bind=engine)

@order_router.get("/")
async def hello(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Token")
    return {"message": "This Is Orders"}


@order_router.post('/order', status_code=status.HTTP_201_CREATED)
async def place_an_order(order: OrderModel, Authorize: AuthJWT = Depends()):
    """
        ## Placing an Order
        This Requires the following
        - quantity: integer
        - pizza_size: string
    """
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Token")

    current_user = Authorize.get_jwt_subject()

    user = session.query(User).filter(User.username==current_user).first()

    new_order = Order(
        pizza_size=order.pizza_size,
        quantity=order.quantity,
    )
    new_order.user=user
    session.add(new_order)
    session.commit()

    response = {
        "pizza_size": new_order.pizza_size,
        "quantity": new_order.quantity,
        "id": new_order.id,
        "order_status": new_order.order_status
    }

    return jsonable_encoder(response)

@order_router.get('/orders')
async def list_all_orders(Authorize: AuthJWT = Depends()):
    """
        ## List All Orders
        This lists all orders made.It can be accessed by superusers
    """
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Token!")

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username==current_user).first()
    if user.is_staff:
        orders = session.query(Order).all()

        return jsonable_encoder(orders)

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="You Are Not A SuperUser!!")
@order_router.get('/orders/{id}')
async def get_order_by_id(id: int, Authorize: AuthJWT = Depends()):
    """
        ## Get an Order By its ID.
        This gets order by its ID. And its only accessed by a superuser
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Token!!")
    user =Authorize.get_jwt_subject()

    current_user = session.query(User).filter(User.username==user).first()

    if current_user.is_staff:
        order = session.query(Order).filter(Order.id==id).first()

        return jsonable_encoder(order)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not allowed to carry out request"
    )
@order_router.get('/user/orders')
async def get_user_orders(Authorize: AuthJWT = Depends()):
    """
          ## Get a current user's orders.
          This lists the orders made by the currently logged users
    """
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token!!"
        )
    user = Authorize.get_jwt_subject()
    current_user = session.qury(User).filter(User.username==user).first()

    return jsonable_encoder(current_user.orders)
@order_router.get('/user/order/{id}/')
async def get_specific_order(id: int, Authorize: AuthJWT = Depends()):
    """
          ## Get A specific order by the currently Logged user.
          This returns an order by ID for the currently logged user
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Token!!"
                            )

    subject = Authorize.get_jwt_subject()

    current_user = session.query(User).filter(User.username==subject).first()

    orders = current_user.orders
    for o in orders:
        if o.id == id:
          return jsonable_encoder(o)

    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                         detail="No Order with such id")


@order_router.put('/order/update/{id}')
async def update_order(id: int, order: OrderModel, Authorize: AuthJWT = Depends()):
    """
          ## Updating an Order.
          This updates and orders requires the following fields
          - quantity: integer
          - pizza_size: string
      """
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Token!!")

    order_to_update = session.query(Order).filter(Order.id == id).first()
    order_to_update.quantity = order.quantity
    order_to_update.pizza_size = order.pizza_size

    session.commit()

    response = {
        "id": order_to_update.id,
        "quantity": order_to_update.quantity,
        "pizza_size": order_to_update.pizza_size,
        "order_status": order_to_update.order_status
    }
    return jsonable_encoder(response)


@order_router.patch('/order/update/{id}')
async def update_order_status(id: int,order: OrderStatusModel, Authorize: AuthJWT = Depends()):
    """
        ## Update an order's status
        This is for updating an orders status and requires an 'order_status' in string format
    """
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Token")
    username = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username==username).first()

    if current_user.is_staff:
        order_to_update = session.query(Order).filter(Order.id==id).first()
        order_to_update.order_status = order.order_status
        session.commit()

        response = {
            "id": order_to_update.id,
            "quantity": order_to_update.quantity,
            "pizza_size": order_to_update.pizza_size,
            "order_status": order_to_update.order_status
        }
        return jsonable_encoder(response)



@order_router.delete('/order/delete/{id}/', status_code=status.HTTP_204_NO_CONTENT)
async def delete_an_order(id: int, Authorize: AuthJWT = Depends()):
    """
        ## Delete an Order
        This delete an order by its ID
    """

    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Token!1"
                            )

    order_to_delete = session.query(Order).filter(Order.id==id).first()
    session.delete(order_to_delete)
    session.commit()

    return order_to_delete