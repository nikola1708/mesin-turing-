from dataclasses import dataclass

@dataclass
class TuringMachine:
    """
    Turing Machine untuk simulasi lampu lalu lintas.

    q0 = Merah
    q1 = Kuning (menuju Hijau)
    q2 = Hijau
    q3 = Kuning (kembali ke Merah)

    Tape digunakan sebagai timer:
    1111 = 4 detik
    1    = 1 detik
    """

    def __init__(self):
        self.state = "q0"
        self.reset_tape()

    def reset_tape(self):
        """
        Membuat tape baru sesuai state aktif.
        """

        if self.state == "q0":  # Merah
            self.tape = list("1111")

        elif self.state == "q1":  # Kuning (menuju Hijau)
            self.tape = list("1")

        elif self.state == "q2":  # Hijau
            self.tape = list("1111")

        elif self.state == "q3":  # Kuning (kembali ke Merah)
            self.tape = list("1")

        self.head = 0

    def step(self):
        """
        Satu langkah Turing Machine.

        Jika masih ada simbol:
            1 -> B

        Jika tape habis:
            pindah state
            buat tape baru
        """

        if self.head < len(self.tape):

            self.tape[self.head] = "B"
            self.head += 1

        else:

            if self.state == "q0":
                self.state = "q1"

            elif self.state == "q1":
                self.state = "q2"

            elif self.state == "q2":
                # after green go to the return-yellow state
                self.state = "q3"

            else:
                # q3 -> q0
                self.state = "q0"

            self.reset_tape()

        return self.state

    def current_color(self):

        return {
            "q0": "red",
            "q1": "yellow",
            "q2": "green",
            "q3": "yellow"
        }[self.state]

    def tape_content(self):

        return "".join(self.tape)

    def head_position(self):

        return self.head


if __name__ == "__main__":

    tm = TuringMachine()

    for i in range(15):

        print(
            f"State={tm.state} | "
            f"Tape={tm.tape_content()} | "
            f"Head={tm.head_position()}"
        )

        tm.step()