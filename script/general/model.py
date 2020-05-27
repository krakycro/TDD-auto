import general.logger as log

##############################################################################

# required key name for every object
CLASS_NAME = "name"

##############################################################################
# ROOT classes
##############################################################################

class Base(object):  # Base class for every item class
    """
    Info: Subclass for automating all working classes
        - creates variables as ClassLoader type
    """

    def _get_members(self):
        """
        Info: get all custom members without name
        """
        return [attr
                for attr in dir(self)
                if not callable(getattr(self, attr))
                and not attr.startswith("__")
                and CLASS_NAME is not attr
                ]

    ##########################################################################
    def __init__(self, name):
        self.name = _ClassLoader(name)

    # ------------------------------------------------------------------------
    def __repr__(self):
        return self.to_string()

    # ------------------------------------------------------------------------
    def __str__(self):
        return self.__repr__()

    # ------------------------------------------------------------------------
    def __iadd__(self, other):
        members = self._get_members()
        for m in members:
            if isinstance(getattr(other, m), _ClassLoader) \
                    and isinstance(getattr(self, m), _ClassLoader):
                attr = getattr(self, m)
                if attr.var is not attr.init and attr.var is not None:
                    c = getattr(other, m)
                    if isinstance(c.var, list):
                        c.var.extend(getattr(self, m).var)

                    if isinstance(c.var, dict):
                        c.var.update(getattr(self, m).var)

                    else:
                        c.var = getattr(self, m)

            else:
                log.log_error(
                    f"Invalid init class: {getattr(other, m)}, "
                    f"for {m}, must be _ClassLoader"
                )

        return other

    # ------------------------------------------------------------------------
    def var_linker(self, elems):
        """
        Info: links all existing members with the same in dict
        """
        members = self._get_members()
        for key, item in elems.items():
            err = True
            for m in members:
                if key == m:  # m[m.find('_') + 1:]:
                    err = False
                    if isinstance(getattr(self, m), _ClassLoader):
                        c = getattr(self, m)
                        if c.init is not item and item is not None:
                            if isinstance(c.var, list):
                                if isinstance(item, list):
                                    exec('self.%s.var.extend(item)' % (m))

                                else:
                                    exec(
                                        'self.%s.var.append("%s")'
                                        % (m, item)
                                    )
                            if isinstance(c.var, dict):
                                if isinstance(item, dict):
                                    exec('self.%s.var.update(item)' % (m))

                                else:
                                    log.log_error(
                                        f"Type is dict but item is not"
                                        f"{self.__class__.__name__}.{key}={item}"
                                    )

                            else:
                                if not isinstance(item, str):
                                    exec('self.%s.var = item' % (m))

                                else:
                                    exec('self.%s.var = "%s"' % (m, item))

                    else:
                        log.log_error(
                            f"Invalid init class: {getattr(self, m)}, "
                            f"for {m}, must be _ClassLoader"
                        )

            if err and "Base" not in self.__class__.__name__:
                log.log_error(
                    f"Variable not found "
                    f"{self.__class__.__name__}.{key}={item}"
                )

    # ------------------------------------------------------------------------
    def to_string(self):
        """
        Info: prints object_name< [member=value,] >
        """
        members = self._get_members()
        return f"{self.__class__.__name__}({self.name.var})@{id(self)}" \
            + "<" \
            + ", ".join([item
                         + " = "
                         + str(getattr(self, item).var) for item in members
                         ]) \
            + ">"

    # ------------------------------------------------------------------------
    def to_dict(self):
        """
        Info: passes dict of {member_name : member_object}
        """
        members = self._get_members()
        temp_dict = {}
        for item in members:
            if isinstance(item, list):
                if issubclass(item.class_type, Base):
                    temp_dict[self.name.var] = \
                        getattr(self, item).var.to_dict()
                else:
                    temp_dict[self.name.var] = item

            else:
                temp_dict[self.name.var] = item

        return [getattr(self, item).var.to_dict() for item in members]

    # ------------------------------------------------------------------------
    def to_obj_list(self):
        """
        Info: passes list of object members
        """
        members = self._get_members()
        return [getattr(self, item) for item in members]


##############################################################################


class _ClassLoader(object):
    """
    Info: class for handling variables
        - types: var, list
        - init value as first var
        - list as nesting objects or reference to them
    """

    def __init__(self, var, class_type=object, true_list=False):
        self.var = var
        self.init = var
        if issubclass(class_type, Base):
            self.class_type = class_type

        else:
            self.class_type = None

        self.true_list = bool(true_list)


##############################################################################
# SAMPLE
##############################################################################

"""
##############################################################################


class Sample(Base):

    def __init__(self, name, var_dict):
        super().__init__(name)
        ...
        # must
        self.var_linker(var_dict)


"""

##############################################################################
# FILE
##############################################################################

class CFile(Base):

    def __init__(self, name, var_dict):
        super().__init__(name)

        self.path = _ClassLoader(None)
        self.objects = _ClassLoader({}, class_type=CObject)

        # must
        self.var_linker(var_dict)


##############################################################################


class CObject(Base):

    def __init__(self, name, var_dict):
        super().__init__(name)

        self.space = _ClassLoader(None)
        self.ret_val = _ClassLoader(None, class_type=CDataType)
        self.fnc_parent = _ClassLoader(None)
        self.fnc_args = _ClassLoader([], class_type=CVariable)
        self.fnc_type = _ClassLoader(None)

        # must
        self.var_linker(var_dict)

##############################################################################


class CVariable(Base):

    def __init__(self, name, var_dict):
        super().__init__(name)

        self.datatype = _ClassLoader(None, class_type=CDataType)
        self.list = _ClassLoader(False)

        # must
        self.var_linker(var_dict)

##############################################################################

class CDataType(Base):

    def __init__(self, name, var_dict):
        super().__init__(name)

        self.is_const = _ClassLoader(False)
        self.var_type = _ClassLoader(None)

        # must
        self.var_linker(var_dict)

##############################################################################
# BUNDLE
##############################################################################

class Bundle(object):
    def __init__(self):
        self.files = {}
        self.objs = {}
        self.vars = {}
        self.dtypes = {}

##############################################################################
##############################################################################

def add_dict(target: dict, output):
    if isinstance(output, dict):
        for key, obj in output.items():
            if key not in target:
                target[key] = obj

            else:
                print(f"Duplicate of: {key}={obj}")
                output[key] = target[key]

        return output

    elif isinstance(output, Base):
        if output not in target:
            target[output.name.var] = output

        else:
            print(f"Duplicate: {output}")
            output = target[output.name.var]

        return output

    else:
        log.log_error(f"Unknown type: {type(output)}:{output}")

    return None

##############################################################################
