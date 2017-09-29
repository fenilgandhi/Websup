<script type="text/javascript">
        jQuery(document).ready(function() {
            validateNumbers();
            $('#mobile_numbers').keyup(function() {
                if (/\D/g.test(this.value)) {
                    this.value = this.value.replace(/\D/g, '');
                }
                this.value = this.value
                    .replace(/[\n\r]+/g, "")
                    .replace(/(.{10})/g, "$1\n");
                validateNumbers();
            });

            function validateNumbers() {
                var value = $("#mobile_numbers").val();
                var numbersArray = value.split('\n');
                var validNumbers = [];
                var duplicateNumbers = [];
                var inValidNumbers = [];
                
                // remove empty elements
                var index = numbersArray.indexOf("");
                while(index !== -1)
                {
                    numbersArray.splice(index,1);
                    index = numbersArray.indexOf("");
                }
                
                for (var $i = 0; $i < numbersArray.length; $i++) {
                    var number = numbersArray[$i];
                    if (validNumbers.indexOf(number) !== -1 || inValidNumbers.indexOf(number) !== -1) {
                        duplicateNumbers.push(number);
                    } else if (number.match(/[789]\d{9}/)) {
                        validNumbers.push(number);
                    } else {
                        inValidNumbers.push(number);
                    }
                }
                $("#total").text(numbersArray.length);
                $("#duplicate").text(duplicateNumbers.length);
                $("#valid").text(validNumbers.length);
                $("#invalid").text(inValidNumbers.length);
            }
        });
</script>