import z3
from tfmc.encoding import get_user_friendly_name

from tfmc.solver_class import SolverContext


def instance_secgroup(s: SolverContext):
    aws_instance, aws_secgroup = z3.Consts("aws_instance aws_secgroup", s.sort.element)
    stmt = z3.And(
        s.fn.category(aws_instance) == s.ref.category["aws_instance"],
        z3.Not(
            z3.Exists(
                [aws_secgroup],
                s.fn.association(
                    aws_instance,
                    s.ref.association["aws_instance::vpc_security_group_ids"],
                    aws_secgroup,
                ),
            )
        ),
        s.solver.ctx,
    )

    s.solver.assert_and_track(stmt, "aws_instance_has_secgroup")

    # Error message
    def error_msg():
        instance_name = get_user_friendly_name(s, aws_instance)
        return f"Instance {instance_name} is not linked to any security group."

    return ("All instances must have at least one security group.", True, error_msg)
