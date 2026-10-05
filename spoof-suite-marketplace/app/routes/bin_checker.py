from flask import Blueprint, request, render_template, flash
from app.utils.bin_checker import check_bin

bin_checker_bp = Blueprint('bin_checker', __name__, url_prefix='/bin-checker')

@bin_checker_bp.route('/', methods=['GET', 'POST'])
def bin_checker():
    result = None
    bin_input = ''
    error = None

    if request.method == 'POST':
        bin_input = request.form.get('bin', '').strip()
        if not bin_input:
            error = "Please enter a BIN."
        elif not bin_input.isdigit() or len(bin_input) < 6:
            error = "BIN must be at least 6 digits and numeric."
        else:
            try:
                result = check_bin(bin_input)
            except Exception as e:
                error = f"Error checking BIN: {e}"

    return render_template('bin_checker.html', result=result, bin_input=bin_input, error=error)