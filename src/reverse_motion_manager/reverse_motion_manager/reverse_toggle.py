#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger
from rcl_interfaces.srv import SetParameters
from rcl_interfaces.msg import Parameter, ParameterValue, ParameterType

def p_bool(name, value):
    return Parameter(
        name=name,
        value=ParameterValue(type=ParameterType.PARAMETER_BOOL, bool_value=bool(value)),
    )

def p_double(name, value):
    return Parameter(
        name=name,
        value=ParameterValue(type=ParameterType.PARAMETER_DOUBLE, double_value=float(value)),
    )

def p_darray(name, values):
    return Parameter(
        name=name,
        value=ParameterValue(type=ParameterType.PARAMETER_DOUBLE_ARRAY, double_array_value=[float(v) for v in values]),
    )

class ReverseToggle(Node):
    def __init__(self):
        super().__init__('reverse_toggle')

        # Targets 
        self.controller_srv = self.create_client(SetParameters, '/controller_server/set_parameters')
        self.smoother_srv   = self.create_client(SetParameters, '/velocity_smoother/set_parameters')

        self.get_logger().info('Waiting for controller_server/set_parameters...')
        self.controller_srv.wait_for_service()
        self.get_logger().info('Waiting for velocity_smoother/set_parameters...')
        self.smoother_srv.wait_for_service()

        self.create_service(Trigger, '/reverse_motion/enable', self.enable_cb)
        self.create_service(Trigger, '/reverse_motion/disable', self.disable_cb)

        self.get_logger().info('ReverseToggle ready. Use /reverse_motion/enable or /reverse_motion/disable')

    def set_params(self, client, params):
        req = SetParameters.Request()
        req.parameters = params
        future = client.call_async(req)
        rclpy.spin_until_future_complete(self, future, timeout_sec=3.0)
        if not future.done():
            return False, "timeout"
        result = future.result()
        
        ok = any(r.successful for r in result.results)
        reason = "; ".join([r.reason for r in result.results if not r.successful]) or "ok"
        return ok, reason

    def enable_cb(self, req, res):
        self.get_logger().info('Enabling reverse motion...')

       
        dwb_params = [
            p_double('FollowPath.min_vel_x', -0.26),   # allow reverse
            p_double('FollowPath.max_vel_x',  0.30),
            p_double('FollowPath.min_speed_xy', 0.0),
            p_double('FollowPath.max_speed_xy', 0.30),
            p_double('FollowPath.acc_lim_x', 3.0),
            p_double('FollowPath.decel_lim_x', -2.5),
            p_double('FollowPath.vx_samples', 20),
        ]
        ok1, reason1 = self.set_params(self.controller_srv, dwb_params)

       
        rpp_params = [
            p_bool('FollowPath.allow_reversing', True),
            p_bool('FollowPath.use_rotate_to_heading', False),
        ]
        ok2, reason2 = self.set_params(self.controller_srv, rpp_params)

       
        smooth_params = [
            p_darray('min_velocity', [-0.5, 0.0, -2.5]),
        ]
        ok3, reason3 = self.set_params(self.smoother_srv, smooth_params)

        if ok1 or ok2:
            res.success = True
            res.message = f"Reverse enabled (controller ok: {ok1 or ok2}, smoother ok: {ok3})"
        else:
            res.success = False
            res.message = f"Failed to enable reverse. reasons: {reason1} | {reason2} | {reason3}"
        return res

    def disable_cb(self, req, res):
        self.get_logger().info('Disabling reverse motion (forward-only)...')

        
        dwb_params = [
            p_double('FollowPath.min_vel_x', 0.0),
            p_double('FollowPath.vx_samples', 20),
        ]
        ok1, reason1 = self.set_params(self.controller_srv, dwb_params)

        
        rpp_params = [
            p_bool('FollowPath.allow_reversing', False),
            p_bool('FollowPath.use_rotate_to_heading', True),
        ]
        ok2, reason2 = self.set_params(self.controller_srv, rpp_params)

        
        smooth_params = [
            p_darray('min_velocity', [0.0, 0.0, -2.5]),
        ]
        ok3, reason3 = self.set_params(self.smoother_srv, smooth_params)

        if ok1 or ok2:
            res.success = True
            res.message = f"Reverse disabled (controller ok: {ok1 or ok2}, smoother ok: {ok3})"
        else:
            res.success = False
            res.message = f"Failed to disable reverse. reasons: {reason1} | {reason2} | {reason3}"
        return res

def main():
    rclpy.init()
    node = ReverseToggle()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

