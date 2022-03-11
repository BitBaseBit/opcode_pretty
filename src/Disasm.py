from __future__ import annotations
import os, sys
from typing import List, Dict, Tuple
import solcx

import os, sys
import json

OP_TO_STR = {
    "00": "STOP",
    "01": "ADD",
    "0a": "EXP",
    "64": "PUSH5",
    "65": "PUSH6",
    "66": "PUSH7",
    "67": "PUSH8",
    "68": "PUSH9",
    "69": "PUSH10",
    "6a": "PUSH11",
    "6b": "PUSH12",
    "6c": "PUSH13",
    "6d": "PUSH14",
    "0b": "SIGNEXTEND",
    "6e": "PUSH15",
    "6f": "PUSH16",
    "70": "PUSH17",
    "71": "PUSH18",
    "72": "PUSH19",
    "73": "PUSH20",
    "74": "PUSH21",
    "75": "PUSH22",
    "76": "PUSH23",
    "77": "PUSH24",
    "78": "PUSH25",
    "79": "PUSH26",
    "7a": "PUSH27",
    "7b": "PUSH28",
    "7c": "PUSH29",
    "7d": "PUSH30",
    "7e": "PUSH31",
    "7f": "PUSH32",
    "80": "DUP1",
    "81": "DUP2",
    "82": "DUP3",
    "83": "DUP4",
    "84": "DUP5",
    "85": "DUP6",
    "86": "DUP7",
    "87": "DUP8",
    "88": "DUP9",
    "89": "DUP10",
    "8a": "DUP11",
    "8b": "DUP12",
    "8c": "DUP13",
    "8d": "DUP14",
    "8e": "DUP15",
    "8f": "DUP16",
    "90": "SWAP1",
    "91": "SWAP2",
    "92": "SWAP3",
    "93": "SWAP4",
    "94": "SWAP5",
    "95": "SWAP6",
    "96": "SWAP7",
    "97": "SWAP8",
    "98": "SWAP9",
    "99": "SWAP10",
    "9a": "SWAP11",
    "9b": "SWAP12",
    "9c": "SWAP13",
    "9d": "SWAP14",
    "9e": "SWAP15",
    "9f": "SWAP16",
    "10": "LT",
    "a0": "LOG0",
    "a1": "LOG1",
    "a2": "LOG2",
    "a3": "LOG3",
    "a4": "LOG4",
    "11": "GT",
    "b0": "PUSH",
    "b1": "DUP",
    "b2": "SWAP",
    "12": "SLT",
    "13": "SGT",
    "02": "MUL",
    "14": "EQ",
    "15": "ISZERO",
    "16": "AND",
    "17": "OR",
    "18": "XOR",
    "f0": "CREATE",
    "f1": "CALL",
    "f2": "CALLCODE",
    "f3": "RETURN",
    "f4": "DELEGATECALL",
    "f5": "CREATE2",
    "19": "NOT",
    "fa": "STATICCALL",
    "fd": "REVERT",
    "ff": "SELFDESTRUCT",
    "1a": "BYTE",
    "1b": "SHL",
    "1c": "SHR",
    "1d": "SAR",
    "03": "SUB",
    "20": "SHA3",
    "04": "DIV",
    "30": "ADDRESS",
    "31": "BALANCE",
    "05": "SDIV",
    "32": "ORIGIN",
    "33": "CALLER",
    "34": "CALLVALUE",
    "35": "CALLDATALOAD",
    "36": "CALLDATASIZE",
    "37": "CALLDATACOPY",
    "38": "CODESIZE",
    "39": "CODECOPY",
    "3a": "GASPRICE",
    "3b": "EXTCODESIZE",
    "06": "MOD",
    "3c": "EXTCODECOPY",
    "3d": "RETURNDATASIZE",
    "3e": "RETURNDATACOPY",
    "3f": "EXTCODEHASH",
    "40": "BLOCKHASH",
    "41": "COINBASE",
    "42": "TIMESTAMP",
    "43": "NUMBER",
    "44": "DIFFICULTY",
    "45": "GASLIMIT",
    "07": "SMOD",
    "46": "CHAINID",
    "47": "SELFBALANCE",
    "48": "BASEFEE",
    "08": "ADDMOD",
    "50": "POP",
    "51": "MLOAD",
    "52": "MSTORE",
    "53": "MSTORE8",
    "54": "SLOAD",
    "55": "SSTORE",
    "56": "JUMP",
    "57": "JUMPI",
    "58": "PC",
    "59": "MSIZE",
    "09": "MULMOD",
    "5a": "GAS",
    "5b": "JUMPDEST",
    "60": "PUSH1",
    "61": "PUSH2",
    "62": "PUSH3",
    "63": "PUSH4"
}
def read_file_json(file_name: str) -> List[str]:
    with open(file_name) as f:
        data = f.readlines()
    abi = []
    for line in data:
        if not "[" in line:
            continue
        else:
            abi.extend(json.loads(line))
    return abi



class InstructionIterator:
    def __init__(self, bytecode):
        self.bytecode = [bytecode[x : x + 2] for x in range(0, len(bytecode), 2)]
        self.op_table = OP_TO_STR
        self.cur_op = self.bytecode[0]
        self.cur_op_str = self.op_str()
        self.arg = []
        self.pc = 0
        self.started = False
        self.error = None

    def next(self) -> bool:
        if len(self.bytecode) <= self.pc or self.error != None:
            return False
        if self.started:
            if self.arg != None:
                self.pc += len(self.arg)
            self.pc += 1
        else:
            self.started = True

        if len(self.bytecode) <= self.pc:
            return False

        self.cur_op = self.bytecode[self.pc]
        self.cur_op_str = self.op_str()
        push_op, size = self.is_push(self.cur_op_str)
        if push_op:
            u = self.pc + size + 1
            if len(self.bytecode) <= self.pc or len(self.bytecode) < u:
                self.error = (
                    f"Incomplete push instruction at {self.pc}\n curr_op: {self.cur_op_str}"
                )
            self.arg = self.bytecode[self.pc + 1 : u]
            self.arg_padded = self.pad_arg(self.arg)
        else:
            self.arg = None
        return True

    def disassemble(self) -> Dict[str, str]:
        self.instructions = {}
        while self.next():
            if self.arg != None and len(self.arg) > 0:
                self.instructions[hex(self.pc)] = f"{self.op_str()} {self.arg_padded}"
            else:
                self.instructions[hex(self.pc)] = f"{self.op_str()}"
        return self.instructions

    def is_push(self, op_str) -> Tuple[bool, int]:
        if "PUSH" in op_str:
            return True, self.push_arg_size(op_str)
        else:
            return False, 0

    def push_arg_size(self, op_str) -> int:
        return int(op_str[op_str.find("H") + 1 :])

    def op_str(self):
        try:
            return self.op_table[self.cur_op]
        except KeyError:
            val = f"INVALID"
            return val

    def pad_arg(self, arg):
        len_push = self.push_arg_size(self.cur_op_str) * 2
        arg_hex = hex(int("".join(arg), 16))
        l_arg = len(arg_hex[2:])
        arg = "0x" + "0" * (len_push - l_arg) + arg_hex[2:]
        return arg



def main():
    bin_path = f"{sys.argv[1][:-4]}.bin"
    _, binary = solcx.compile_files([sys.argv[1]], output_values=['bin']).popitem()
    it = InstructionIterator(binary['bin']) 
    dis = it.disassemble()
    with open(bin_path, 'w') as f:
        for key, value in dis.items():
            f.write(f"{key}: {value}\n")

main()